"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { cancelOrder, fetchOrders } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";

const DEFAULT_RESTAURANT_IMAGE =
  "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=900&q=80";

export default function OrdersPage() {
  const router = useRouter();
  const { isAuthenticated, loading } = useAuth();
  const [orders, setOrders] = useState<any[]>([]);
  const [fetching, setFetching] = useState(true);

  useEffect(() => {
    if (loading) {
      return;
    }

    if (!isAuthenticated) {
      router.push("/login");
      return;
    }

    async function loadOrders() {
      try {
        const data = await fetchOrders();
        setOrders(data.orders || []);
      } catch (error) {
        router.push("/login");
      } finally {
        setFetching(false);
      }
    }

    loadOrders();
  }, [isAuthenticated, loading, router]);

  if (loading || fetching) {
    return <div className="p-10 text-center">Loading orders...</div>;
  }

  const statusClasses: Record<string, string> = {
    placed: "bg-yellow-100 text-yellow-800",
    confirmed: "bg-blue-100 text-blue-800",
    preparing: "bg-orange-100 text-orange-800",
    ready: "bg-purple-100 text-purple-800",
    picked_up: "bg-indigo-100 text-indigo-800",
    on_the_way: "bg-violet-100 text-violet-800",
    delivered: "bg-green-100 text-green-800",
    cancelled: "bg-red-100 text-red-800",
  };

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

  const timelineSteps = ["placed", "confirmed", "preparing", "on_the_way", "delivered"];
  const stepClasses: Record<string, string> = {
    placed: "bg-yellow-100 text-yellow-800",
    confirmed: "bg-blue-100 text-blue-800",
    preparing: "bg-orange-100 text-orange-800",
    on_the_way: "bg-violet-100 text-violet-800",
    delivered: "bg-green-100 text-green-800",
  };
  const getStepIndex = (status: string) => timelineSteps.indexOf(status);

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-5xl mx-auto rounded-3xl bg-white p-8 shadow-xl">
        <h1 className="text-4xl font-bold mb-6">Your Orders</h1>
        {orders.length === 0 ? (
          <div className="text-center text-gray-500 py-16">No orders yet.</div>
        ) : (
          <div className="space-y-6">
            {orders.map((order) => (
              <div key={order.order_id} className="border rounded-3xl p-6 shadow-sm">
                <div className="flex flex-col md:flex-row justify-between gap-4 mb-4">
                  <div className="flex items-center gap-4">
                    <img
                      src={order.restaurant?.image || DEFAULT_RESTAURANT_IMAGE}
                      alt={order.restaurant?.name || "Restaurant"}
                      className="h-20 w-20 rounded-3xl object-cover"
                      onError={(event) => {
                        const target = event.currentTarget as HTMLImageElement;
                        if (target.src !== DEFAULT_RESTAURANT_IMAGE) {
                          target.src = DEFAULT_RESTAURANT_IMAGE;
                        }
                      }}
                    />
                    <div>
                      <div className="text-xl font-bold">Order #{order.order_id}</div>
                      <div className="text-gray-500">{order.restaurant?.name || order.restaurant_id}</div>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <span className={`px-3 py-1 rounded-full font-semibold ${statusClasses[order.status] || "bg-gray-100 text-gray-800"}`}>
                      {statusLabel[order.status] || order.status}
                    </span>
                    <div className="text-orange-500 font-bold text-xl">₹{order.total_amount}</div>
                  </div>
                </div>

                <div className="grid gap-2 text-sm text-gray-600 mb-6">
                  <div>
                    Payment: <span className="bg-green-100 text-green-700 px-2 py-1 rounded">COD</span>
                  </div>
                  <div>Placed: {new Date(order.created_at).toLocaleString()}</div>
                </div>

                <div className="space-y-3 mb-6">
                  {order.items.map((item: any) => (
                    <div key={item.id} className="flex justify-between text-lg">
                      <span>{item.name} × {item.quantity}</span>
                      <span>₹{item.price * item.quantity}</span>
                    </div>
                  ))}

                  <div className="border-t pt-4 flex justify-between font-semibold text-lg">
                    <span>Total</span>
                    <span>₹{order.total_amount}</span>
                  </div>
                </div>

                <div className="flex flex-col sm:flex-row justify-between gap-3 items-start sm:items-center">
                  <button
                    onClick={() => router.push(`/orders/${order.order_id}`)}
                    className="bg-orange-500 text-white px-4 py-2 rounded-lg hover:bg-orange-600 transition"
                  >
                    Track Order
                  </button>
                  {order.status === "placed" ? (
                    <button
                      onClick={async () => {
                        try {
                          await cancelOrder(order.order_id);
                          setOrders((prev) => prev.map((o) => o.order_id === order.order_id ? { ...o, status: "cancelled" } : o));
                        } catch (error) {
                          console.error(error);
                          alert("Unable to cancel order.");
                        }
                      }}
                      className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition"
                    >
                      Cancel Order
                    </button>
                  ) : null}
                </div>

                <div className="mt-6 grid gap-2 text-sm text-gray-700">
                  <div className="flex gap-2 items-center">
                    <span className="font-semibold">Timeline:</span>
                    <span>{statusLabel[order.status] || order.status}</span>
                  </div>
                  <div className="grid gap-1">
                    {timelineSteps.map((step, stepIndex) => {
                      const currentStepIndex = getStepIndex(order.status);
                      const complete = currentStepIndex >= 0 && stepIndex <= currentStepIndex;
                      const stepClass = complete ? stepClasses[step] : "bg-gray-100 text-gray-500";
                      return (
                        <div key={step} className="flex flex-wrap items-center gap-3 text-sm">
                          <span className={`${stepClass} px-2 py-1 rounded-full font-semibold`}>
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
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
