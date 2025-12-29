// types/product.ts
export type Product = {
  supermarket: string;
  id: number;
  sku: string;
  url: string;
  brand: string | null;
  product_name_du: string;
  product_name_en: string;
  unit_du: string;
  unit_qty: number;
  unit_type_en: string;
  regular_price: number;
  current_price: number;
  unit_price: number;
  similarity: number;
};
