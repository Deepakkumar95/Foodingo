"use client";

import { usePathname } from "next/navigation";
import { useCart, CartItem } from "@/context/CartContext";

export default function CartSidebar() {
  const pathname = usePathname();
  const {
    cartItems,
    increaseQuantity,
    decreaseQuantity,
    removeFromCart,
  } = useCart();

  if (pathname === "/orders") {
    return null;
  }

  const total = cartItems.reduce(
    (sum: number, item: CartItem) =>
      sum + item.price * item.quantity,
    0
  );

  return (
    <aside className="p-6 bg-white shadow-xl rounded-3xl w-full max-w-md">
      <div className="flex items-center justify-between mb-8">
        <h2 className="text-3xl font-bold">Cart</h2>
      </div>

      {cartItems.length === 0 ? (
        <div className="text-center py-16 text-gray-500">
          Cart is empty
        </div>
      ) : (
        <>
          <div className="space-y-4">
            {cartItems.map((item: CartItem) => (
              <div
                key={item.id}
                className="border rounded-3xl p-4"
              >
                <div className="flex justify-between items-start gap-4">
                  <div>
                    <h3 className="text-lg font-semibold">
                      {item.name}
                    </h3>
                    <p className="text-orange-500 font-bold mt-2">
                      ₹{item.price * item.quantity}
                    </p>
                  </div>

                  <button
                    onClick={() => removeFromCart(item.id)}
                    className="text-red-500 text-sm"
                  >
                    Remove
                  </button>
                </div>

                <div className="flex items-center gap-3 mt-4">
                  <button
                    onClick={() => decreaseQuantity(item.id)}
                    className="bg-gray-200 px-3 py-1 rounded-lg"
                  >
                    -
                  </button>

                  <span className="text-lg font-bold">
                    {item.quantity}
                  </span>

                  <button
                    onClick={() => increaseQuantity(item.id)}
                    className="bg-orange-500 text-white px-3 py-1 rounded-lg"
                  >
                    +
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div className="border-t mt-8 pt-6">
            <div className="flex justify-between text-xl font-bold">
              <span>Total</span>
              <span>₹{total}</span>
            </div>

            <button
              onClick={() =>
                (window.location.href = "/checkout")
              }
              className="mt-6 w-full bg-orange-500 text-white py-3 rounded-2xl text-xl hover:bg-orange-600 transition"
            >
              Checkout
            </button>
          </div>
        </>
      )}
    </aside>
  );
}
