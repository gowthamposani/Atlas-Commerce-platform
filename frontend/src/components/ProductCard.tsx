import { Heart, ShoppingCart, Store } from "lucide-react";
import { Link } from "react-router-dom";

import { ProductListItem } from "../types/api";
import { money } from "../utils/money";

interface ProductCardProps {
  product: ProductListItem;
  onWishlist?: (productId: string) => void;
  onCart?: (productId: string) => void;
}

export function ProductCard({ product, onWishlist, onCart }: ProductCardProps) {
  const primaryImage = product.images.find((image) => image.is_primary) ?? product.images[0];

  return (
    <article className="overflow-hidden rounded-md border border-slate-200 bg-white shadow-sm">
      <Link to={`/products/${product.id}`} className="block">
        {primaryImage ? (
          <img
            src={primaryImage.url}
            alt={primaryImage.alt_text ?? product.name}
            className="aspect-[4/3] w-full object-cover"
          />
        ) : (
          <div className="flex aspect-[4/3] items-center justify-center bg-slate-100 text-sm text-slate-500">
            Product image
          </div>
        )}
      </Link>
      <div className="grid gap-3 p-4">
        <div>
          <Link
            to={`/products/${product.id}`}
            className="line-clamp-2 text-base font-semibold text-slate-950 hover:text-teal-700"
          >
            {product.name}
          </Link>
          <Link
            to={`/stores/${product.seller_id}`}
            className="mt-1 inline-flex items-center gap-1 text-xs font-medium text-slate-500 hover:text-teal-700"
          >
            <Store size={13} aria-hidden="true" />
            {product.seller.store_name}
          </Link>
        </div>
        <div className="flex items-center justify-between gap-3">
          <span className="text-lg font-bold text-slate-950">{money(product.base_price)}</span>
          <span className="rounded-md bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-600">
            {product.category.name}
          </span>
        </div>
        {(onWishlist || onCart) && (
          <div className="grid grid-cols-2 gap-2">
            {onWishlist && (
              <button
                type="button"
                className="secondary-button"
                onClick={() => onWishlist(product.id)}
              >
                <Heart size={15} aria-hidden="true" />
                Wishlist
              </button>
            )}
            {onCart && (
              <button type="button" className="primary-button" onClick={() => onCart(product.id)}>
                <ShoppingCart size={15} aria-hidden="true" />
                Cart
              </button>
            )}
          </div>
        )}
      </div>
    </article>
  );
}
