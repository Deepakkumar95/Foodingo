"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getOrder } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";

const trackingSteps = [
  "Restaurant",
  "Preparing",
  "Driver Assigned",
  "Live Location",
  "Delivered",
];

const statusToStepIndex: Record<string, number> = {
  placed: 0,
  confirmed: 1,
  preparing: 2,
  on_the_way: 3,
  delivered: 4,
  cancelled: 4,
};

export default function OrderTrackPage({ params }: { params: { id: string } }) {
  const { id } = params;
  const router = useRouter();
  const { isAuthenticated, loading } = useAuth();
  const [order, setOrder] = useState<any>(null);
  const [fetching, setFetching] = useState(true);
  const [error, setError] = useState("");

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
        setError("Unable to load tracking details.");
      } finally {
        setFetching(false);
      }
    }

    loadOrder();
  }, [id, isAuthenticated, loading, router]);

  if (loading || fetching) {
    return <div className="p-10 text-center">Loading tracking details...</div>;
  }

  if (error) {
    return <div className="p-10 text-center text-red-500">{error}</div>;
  }

  if (!order) {
    return <div className="p-10 text-center">Order not found.</div>;
  }

  const currentStepIndex = statusToStepIndex[order.status] ?? 0;
  const formatOrderRef = (id: string) => `#${id.toString().slice(-4)}`;

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-5xl mx-auto rounded-3xl bg-white p-8 shadow-xl">
        <div className="flex flex-col md:flex-row justify-between gap-4 mb-6">
          <div>
            <h1 className="text-4xl font-bold">Tracking {formatOrderRef(order.order_id)}</h1>
            <p className="text-gray-500 mt-2">{order.restaurant?.name || order.restaurant_id}</p>
            <p className="text-gray-700 mt-4 text-lg">{order.restaurant?.name ? `Delivering from ${order.restaurant.name}` : "Restaurant details"}</p>
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-500">Total</div>
            <div className="text-3xl font-bold text-orange-500">₹{order.total_amount}</div>
          </div>
        </div>

        <div className="rounded-3xl border p-6 mb-6">
          <h2 className="text-2xl font-bold mb-4">Live Tracking</h2>
          <div className="grid gap-4 md:grid-cols-5">
            {trackingSteps.map((step, index) => {
              const completed = index <= currentStepIndex;
              return (
                <div key={step} className="text-center">
                  <div className={`mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full ${completed ? "bg-orange-500 text-white" : "bg-gray-100 text-gray-500"}`}>
                    {index + 1}
                  </div>
                  <div className={`text-sm font-semibold ${completed ? "text-orange-600" : "text-gray-500"}`}>
                    {step}
                  </div>
                </div>
              );
            })}
          </div>
          <div className="mt-6 rounded-3xl bg-slate-50 p-4 text-sm text-slate-700">
            <p className="font-semibold">Current stage:</p>
            <p>{trackingSteps[currentStepIndex] || "Preparing"}</p>
          </div>
        </div>

        <div className="grid gap-6 md:grid-cols-[1.5fr_1fr]">
          <div className="rounded-3xl border p-6">
            <h2 className="text-2xl font-bold mb-4">Order Summary</h2>
            <div className="space-y-4">
              {order.items.map((item: any) => (
                <div key={item.id} className="flex justify-between">
                  <div>
                    <div className="font-semibold">{item.name}</div>
                    <div className="text-sm text-gray-500">Qty: {item.quantity}</div>
                  </div>
                  <div className="font-semibold">₹{item.price * item.quantity}</div>
                </div>
              ))}
            </div>
            <div className="border-t mt-6 pt-4 flex justify-between font-semibold text-lg">
              <span>Total</span>
              <span>₹{order.total_amount}</span>
            </div>
          </div>

          <div className="rounded-3xl border p-6">
            <h2 className="text-2xl font-bold mb-4">Details</h2>
            <div className="space-y-3 text-sm text-gray-700">
              <div className="flex justify-between">
                <span>Status</span>
                <span>{order.status.replace(/_/g, " ")}</span>
              </div>
              <div className="flex justify-between">
                <span>Payment</span>
                <span>COD</span>
              </div>
              <div className="flex justify-between">
                <span>Placed</span>
                <span>{new Date(order.created_at).toLocaleString()}</span>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-8 flex flex-wrap gap-4">
          <button
            onClick={() => router.push("/orders")}
            className="bg-gray-200 text-gray-800 px-4 py-2 rounded-lg hover:bg-gray-300 transition"
          >
            Back to Orders
          </button>
          <button
            onClick={() => router.push(`/orders/${order.order_id}`)}
            className="bg-orange-500 text-white px-4 py-2 rounded-lg hover:bg-orange-600 transition"
          >
            View Details
          </button>
        </div>
      </div>
    </div>
  );
}
