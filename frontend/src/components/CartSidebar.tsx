"use client";

import {
  useEffect,
  useState,
} from "react";

import { useCart } from "@/context/CartContext";

export default function CartSidebar() {
  const [isOpen, setIsOpen] =
    useState(false);

  const {
    cartItems,
    increaseQuantity,
    decreaseQuantity,
    removeFromCart,
  } = useCart();

  // LOCK BODY SCROLL
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow =
        "hidden";
    } else {
      document.body.style.overflow =
        "auto";
    }

    return () => {
      document.body.style.overflow =
        "auto";
    };
  }, [isOpen]);

  // TOTAL PRICE
  const total = cartItems.reduce(
    (sum: number, item: any) =>
      sum +
      item.price * item.quantity,
    0
  );

  // TOTAL ITEMS
  const itemCount = cartItems.reduce(
    (sum: number, item: any) =>
      sum + item.quantity,
    0
  );

  return (
    <>
      {/* MOBILE FLOATING BUTTON */}
      <button
        onClick={() =>
          setIsOpen(!isOpen)
        }
        className="
          fixed bottom-6 right-6 z-50
          bg-orange-500 text-white
          px-5 py-4 rounded-full
          shadow-2xl
          flex items-center gap-2
          md:hidden
          hover:scale-105 transition
        "
      >
        🛒

        <span className="font-bold">
          {itemCount}
        </span>
      </button>

      {/* OVERLAY */}
      <div
        onClick={() =>
          setIsOpen(false)
        }
        className={`
          fixed inset-0 bg-black/40 z-40
          transition-opacity duration-300
          md:hidden
          ${
            isOpen
              ? "opacity-100 visible"
              : "opacity-0 invisible"
          }
        `}
      />

      {/* CART DRAWER */}
      <div
        className={`
          fixed top-0 right-0 h-full
          w-80 bg-white z-50
          shadow-2xl
          p-6
          overflow-y-auto
          transition-transform duration-300 ease-in-out

          ${
            isOpen
              ? "translate-x-0"
              : "translate-x-full"
          }

          md:translate-x-0
        `}
      >
        {/* HEADER */}
        <div className="flex justify-between items-center mb-8">
          <h2 className="text-4xl font-bold">
            Cart
          </h2>

          <button
            onClick={() =>
              setIsOpen(false)
            }
            className="
              md:hidden
              text-gray-500
              text-lg
            "
          >
            ✕
          </button>
        </div>

        {/* EMPTY CART */}
        {cartItems.length === 0 ? (
          <div className="text-center mt-20">
            <p className="text-gray-500 text-xl">
              Your cart is empty
            </p>
          </div>
        ) : (
          <>
            {/* CART ITEMS */}
            <div className="space-y-4">
              {cartItems.map(
                (item: any) => (
                  <div
                    key={item.id}
                    className="
                      border rounded-2xl
                      p-4
                    "
                  >
                    <div className="flex justify-between">
                      <div>
                        <h3 className="font-bold text-xl">
                          {item.name}
                        </h3>

                        <p className="text-orange-500 font-bold mt-2">
                          ₹
                          {item.price *
                            item.quantity}
                        </p>
                      </div>

                      <button
                        onClick={() =>
                          removeFromCart(
                            item.id
                          )
                        }
                        className="
                          text-red-500
                          text-sm
                        "
                      >
                        Remove
                      </button>
                    </div>

                    {/* QUANTITY */}
                    <div className="flex items-center gap-4 mt-4">
                      <button
                        onClick={() =>
                          decreaseQuantity(
                            item.id
                          )
                        }
                        className="
                          bg-gray-200
                          w-10 h-10
                          rounded-xl
                          text-xl
                        "
                      >
                        -
                      </button>

                      <span className="text-xl font-bold">
                        {item.quantity}
                      </span>

                      <button
                        onClick={() =>
                          increaseQuantity(
                            item.id
                          )
                        }
                        className="
                          bg-orange-500
                          text-white
                          w-10 h-10
                          rounded-xl
                          text-xl
                        "
                      >
                        +
                      </button>
                    </div>
                  </div>
                )
              )}
            </div>

            {/* TOTAL */}
            <div className="border-t mt-8 pt-6">
              <div className="flex justify-between text-3xl font-bold">
                <span>Total</span>

                <span>
                  ₹{total}
                </span>
              </div>

              <button
                className="
                  mt-6 w-full
                  bg-orange-500
                  text-white
                  py-4 rounded-2xl
                  text-xl
                  hover:bg-orange-600
                  transition
                "
              >
                Checkout
              </button>
            </div>
          </>
        )}
      </div>
    </>
  );
}