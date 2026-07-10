import {
  PropsWithChildren,
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "../services/api";
import {
  CurrentUser,
  LoginPayload,
  RegisterPayload,
  TokenResponse,
} from "../types/api";
import {
  clearTokens,
  getAccessToken,
  getRefreshToken,
  setTokens,
} from "../utils/tokenStorage";

interface AuthContextValue {
  user: CurrentUser | undefined;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (payload: LoginPayload) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

async function fetchCurrentUser(): Promise<CurrentUser> {
  const response = await api.get<CurrentUser>("/auth/me");
  return response.data;
}

export function AuthProvider({ children }: PropsWithChildren) {
  const queryClient = useQueryClient();
  const [hasToken, setHasToken] = useState(() => Boolean(getAccessToken()));

  const currentUserQuery = useQuery({
    queryKey: ["auth", "me"],
    queryFn: fetchCurrentUser,
    enabled: hasToken,
  });

  useEffect(() => {
    if (currentUserQuery.isError) {
      clearTokens();
      setHasToken(false);
    }
  }, [currentUserQuery.isError]);

  const value = useMemo<AuthContextValue>(
    () => ({
      user: currentUserQuery.data,
      isAuthenticated: hasToken && Boolean(currentUserQuery.data),
      isLoading: hasToken && currentUserQuery.isLoading,
      login: async (payload: LoginPayload) => {
        const response = await api.post<TokenResponse>("/auth/login", payload);
        setTokens(response.data.access_token, response.data.refresh_token);
        queryClient.setQueryData(["auth", "me"], response.data.user);
        setHasToken(true);
      },
      register: async (payload: RegisterPayload) => {
        await api.post<CurrentUser>("/auth/register", payload);
      },
      logout: async () => {
        const refreshToken = getRefreshToken();
        if (refreshToken) {
          await api.post("/auth/logout", { refresh_token: refreshToken }).catch(() => undefined);
        }
        clearTokens();
        setHasToken(false);
        queryClient.clear();
      },
    }),
    [currentUserQuery.data, currentUserQuery.isLoading, hasToken, queryClient],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return context;
}
