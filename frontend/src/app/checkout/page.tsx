"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useCart } from "@/context/CartContext";
import { useAuth } from "@/context/AuthContext";
import { placeOrder } from "@/lib/api";

export default function CheckoutPage() {
  const router = useRouter();
  const { cartItems, clearCart } = useCart();
  const { isAuthenticated } = useAuth();
  const [address, setAddress] = useState("");
  const [paymentMethod, setPaymentMethod] = useState("COD");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthenticated, router]);

  const subtotal = cartItems.reduce(
    (sum: number, item: any) => sum + item.price * item.quantity,
    0
  );

  const deliveryFee = 40;
  const gst = Math.round(subtotal * 0.05);
  const total = subtotal + deliveryFee + gst;

  async function handlePlaceOrder() {
    if (!address) {
      setError("Please enter delivery address");
      return;
    }

    try {
      await placeOrder({
        restaurant_id: cartItems[0]?.restaurant_id || "",
        delivery_address: {
          address_line: address,
          latitude: 0,
          longitude: 0,
        },
        items: cartItems.map((item: any) => ({
          id: item.id,
          name: item.name,
          quantity: item.quantity,
          price: item.price,
        })),
      });

      clearCart();
      router.push("/success");
    } catch (err: any) {
      setError(err?.message || "Order placement failed");
    }
  }

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-6xl mx-auto grid gap-8 lg:grid-cols-[1.5fr_1fr]">
        <div className="space-y-8">
          <div className="rounded-3xl bg-white p-8 shadow-xl">
            <h1 className="text-4xl font-bold mb-6">Checkout</h1>

            <div className="space-y-4">
              <label className="block text-lg font-semibold">
                Delivery Address
              </label>
              <textarea
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                placeholder="Enter your full address"
                className="w-full h-40 border rounded-2xl p-4 text-lg outline-none"
              />
            </div>

            <div className="mt-8 rounded-3xl border p-6">
              <h2 className="text-2xl font-bold mb-4">Payment Method</h2>
              <div className="space-y-3">
                {["COD"].map((method) => (
                  <label
                    key={method}
                    className="flex items-center gap-3 text-lg"
                  >
                    <input
                      type="radio"
                      name="paymentMethod"
                      value={method}
                      checked={paymentMethod === method}
                      onChange={(e) => setPaymentMethod(e.target.value)}
                      className="h-5 w-5"
                    />
                    {method}
                  </label>
                ))}
              </div>
            </div>
            {error ? <div className="text-red-500 mt-4">{error}</div> : null}
          </div>
        </div>

        <div className="space-y-6">
          <div className="rounded-3xl bg-white p-8 shadow-xl">
            <h2 className="text-3xl font-bold mb-6">Order Summary</h2>

            <div className="space-y-4">
              {cartItems.map((item: any) => (
                <div
                  key={item.id}
                  className="flex items-center justify-between"
                >
                  <div>
                    <p className="font-semibold">{item.name}</p>
                    <p className="text-sm text-gray-500">Qty: {item.quantity}</p>
                  </div>
                  <p className="font-semibold">₹{item.price * item.quantity}</p>
                </div>
              ))}
            </div>

            <div className="mt-8 space-y-3 border-t pt-6 text-lg">
              <div className="flex justify-between">
                <span>Subtotal</span>
                <span>₹{subtotal}</span>
              </div>
              <div className="flex justify-between">
                <span>Delivery Fee</span>
                <span>₹{deliveryFee}</span>
              </div>
              <div className="flex justify-between">
                <span>GST</span>
                <span>₹{gst}</span>
              </div>
              <div className="flex justify-between text-xl font-bold">
                <span>Total</span>
                <span>₹{total}</span>
              </div>
            </div>

            <button
              onClick={handlePlaceOrder}
              className="mt-6 w-full bg-orange-500 text-white py-4 rounded-2xl text-xl hover:bg-orange-600 transition"
            >
              Place Order
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
