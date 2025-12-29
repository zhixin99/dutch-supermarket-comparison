import type { Product } from "./types/product";


type Props = {
  product: Product;
};

export default function ProductCard({ product }: Props) {
  return (
    <a
      href={product.url}
      target="_blank"
      className="
        rounded-2xl bg-white shadow
        hover:shadow-lg transition
        p-4 flex flex-col gap-2
      "
    >
      {/* 超市 + 品牌 */}
      <div className="text-xs text-gray-500">
        {product.supermarket.toUpperCase()}
        {product.brand && ` · ${product.brand}`}
      </div>

      {/* 产品名 */}
      <div className="font-medium leading-snug">
        {product.product_name_du}
      </div>

      {/* 价格 */}
      <div className="mt-auto">
        <div className="text-lg font-semibold">
          €{product.current_price.toFixed(2)}
        </div>
        <div className="text-sm text-orange-600">
          €{product.unit_price.toFixed(2)} / {product.unit_type_en}
        </div>
      </div>
    </a>
  );
}
