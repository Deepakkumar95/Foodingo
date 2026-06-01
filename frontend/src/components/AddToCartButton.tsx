"use client";

import { useCart, CartProduct } from "@/context/CartContext";

export default function AddToCartButton({
  item,
}: {
  item: CartProduct;
}) {
  const { addToCart } = useCart();

  return (
    <button
      onClick={() => {
        addToCart(item);
        alert(`${item.name} added to cart`);
      }}
      className="bg-orange-500 text-white px-4 py-2 rounded-xl hover:bg-orange-600 transition"
    >
      Add to Cart
    </button>
  );
}