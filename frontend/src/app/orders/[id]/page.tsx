"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { cancelOrder, getOrder } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";

export default function OrderDetailPage({ params }: { params: { id: string } }) {
  const { id } = params;
  const router = useRouter();
  const { isAuthenticated, loading } = useAuth();
  const [order, setOrder] = useState<any>(null);
  const [fetching, setFetching] = useState(true);
  const [error, setError] = useState("");
  const [cancelling, setCancelling] = useState(false);

  useEffect(() => {
    if (loading) return;
    if (!isAuthenticated) {
      router.push("/login");
      return;
    }

    async function loadOrder() {
      try {
        const response = await getOrder(id);
        const data = response.order || response;
        setOrder(data);
      } catch (err) {
        setError("Unable to load order details.");
      } finally {
        setFetching(false);
      }
    }

    loadOrder();
  }, [id, isAuthenticated, loading, router]);

  if (loading || fetching) {
    return <div className="p-10 text-center">Loading order...</div>;
  }

  if (error) {
    return <div className="p-10 text-center text-red-500">{error}</div>;
  }

  if (!order) {
    return <div className="p-10 text-center">Order not found.</div>;
  }

  const statusLabel: Record<string, string> = {
    placed: "Placed",
    confirmed: "Confirmed",
    preparing: "Preparing",
    ready: "Ready",
    picked_up: "Picked Up",
    on_the_way: "On the Way",
    delivered: "Delivered",
    cancelled: "Cancelled",
  };

  const stepClasses: Record<string, string> = {
    placed: "bg-yellow-100 text-yellow-800",
    confirmed: "bg-blue-100 text-blue-800",
    preparing: "bg-orange-100 text-orange-800",
    ready: "bg-purple-100 text-purple-800",
    picked_up: "bg-indigo-100 text-indigo-800",
    on_the_way: "bg-violet-100 text-violet-800",
    delivered: "bg-green-100 text-green-800",
    cancelled: "bg-red-100 text-red-800",
  };

  const steps = ["placed", "confirmed", "preparing", "ready", "picked_up", "on_the_way", "delivered"];
  const currentIndex = steps.indexOf(order.status);
  const formatOrderRef = (id: string) => `#${id.toString().slice(-4)}`;

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-5xl mx-auto rounded-3xl bg-white p-8 shadow-xl">
        <div className="flex flex-col md:flex-row justify-between gap-4 mb-6">
          <div>
            <h1 className="text-4xl font-bold">Track Order {formatOrderRef(order.order_id)}</h1>
            <p className="text-gray-500 mt-2">{order.restaurant?.name || order.restaurant_id}</p>
            <div className="mt-3 flex flex-wrap items-center gap-2 text-sm">
              <span className="font-semibold">Payment:</span>
              <span className="bg-green-100 text-green-700 px-2 py-1 rounded-full">COD</span>
            </div>
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-500">Placed</div>
            <div className="text-2xl font-bold">₹{order.total_amount}</div>
          </div>
        </div>

        <div className="grid gap-6 md:grid-cols-[1.5fr_1fr]">
          <div className="space-y-6">
            <div className="rounded-3xl border p-6">
              <h2 className="text-2xl font-bold mb-4">Order Summary</h2>
              <div className="space-y-3">
                {order.items.map((item: any) => (
                  <div key={item.id} className="flex justify-between">
                    <div>
                      <div className="font-semibold">{item.name}</div>
                      <div className="text-sm text-gray-500">Qty: {item.quantity}</div>
                    </div>
                    <div>₹{item.price * item.quantity}</div>
                  </div>
                ))}
              </div>
              <div className="border-t mt-6 pt-4 text-lg font-semibold flex justify-between">
                <span>Total</span>
                <span>₹{order.total_amount}</span>
              </div>
            </div>

            <div className="rounded-3xl border p-6">
              <h2 className="text-2xl font-bold mb-4">Delivery Address</h2>
              <p>{order.delivery_address?.address_line || "N/A"}</p>
              <p className="text-sm text-gray-500 mt-2">
                Lat: {order.delivery_address?.latitude || 0}, Lon: {order.delivery_address?.longitude || 0}
              </p>
            </div>
          </div>

          <div className="rounded-3xl border p-6">
            <h2 className="text-2xl font-bold mb-4">Order Timeline</h2>
            <div className="space-y-3">
              {steps.map((step, index) => {
                const complete = index <= currentIndex;
                const badgeClass = complete ? stepClasses[step] : "bg-gray-100 text-gray-500";
                return (
                  <div key={step} className="flex items-center gap-3">
                    <span className={`${badgeClass} px-3 py-1 rounded-full font-semibold`}>
                      {statusLabel[step]}
                    </span>
                    <span className={complete ? "text-orange-500" : "text-gray-400"}>
                      {complete ? "✓" : "⬜"}
                    </span>
                  </div>
                );
              })}
              {order.status === "cancelled" ? (
                <div className="flex items-center gap-3 text-red-500 font-semibold">
                  <span>⚠️</span>
                  <span>Order cancelled.</span>
                </div>
              ) : null}
            </div>
          </div>
        </div>

        <div className="mt-8 flex gap-4 flex-wrap">
          <button
            onClick={() => router.push("/orders")}
            className="bg-gray-200 text-gray-800 px-4 py-2 rounded-lg hover:bg-gray-300 transition"
          >
            Back to Orders
          </button>
          {order.status === "placed" ? (
            <button
              onClick={() => router.push("/orders")}
              className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition"
            >
              Cancel Order
            </button>
          ) : null}
        </div>
      </div>
    </div>
  );
}
