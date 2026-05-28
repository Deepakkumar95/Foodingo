"use client";

import { useCart } from "@/context/CartContext";

export default function CartSidebar() {
  const {
    cartItems,
    increaseQuantity,
    decreaseQuantity,
    removeFromCart,
  } = useCart();

  // TOTAL PRICE
  const total = cartItems.reduce(
    (sum: number, item: any) =>
      sum + item.price * item.quantity,
    0
  );

  return (
    <div className="fixed right-0 top-0 h-screen w-80 bg-white shadow-2xl p-6 overflow-y-auto">
      <h2 className="text-4xl font-bold mb-8">
        Cart
      </h2>

      {cartItems.length === 0 ? (
        <p className="text-gray-500">
          Cart is empty
        </p>
      ) : (
        <>
          <div className="space-y-4">
            {cartItems.map((item: any) => (
              <div
                key={item.id}
                className="border rounded-2xl p-4"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-bold text-xl">
                      {item.name}
                    </h3>

                    <p className="text-orange-500 font-bold mt-2">
                      ₹
                      {item.price * item.quantity}
                    </p>
                  </div>

                  <button
                    onClick={() =>
                      removeFromCart(item.id)
                    }
                    className="text-red-500 text-sm"
                  >
                    Remove
                  </button>
                </div>

                {/* QUANTITY CONTROLS */}
                <div className="flex items-center gap-4 mt-4">
                  <button
                    onClick={() =>
                      decreaseQuantity(item.id)
                    }
                    className="bg-gray-200 px-3 py-1 rounded-lg"
                  >
                    -
                  </button>

                  <span className="text-xl font-bold">
                    {item.quantity}
                  </span>

                  <button
                    onClick={() =>
                      increaseQuantity(item.id)
                    }
                    className="bg-orange-500 text-white px-3 py-1 rounded-lg"
                  >
                    +
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* TOTAL */}
          <div className="border-t mt-8 pt-6">
            <div className="flex justify-between text-3xl font-bold">
              <span>Total</span>

              <span>₹{total}</span>
            </div>

            <button className="mt-6 w-full bg-orange-500 text-white py-4 rounded-2xl text-xl hover:bg-orange-600 transition">
              Checkout
            </button>
          </div>
        </>
      )}
    </div>
  );
}