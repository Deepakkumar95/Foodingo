"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getAdminOrders, updateOrderStatus } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";

export default function AdminPage() {
  const router = useRouter();
  const { isAuthenticated, loading, user } = useAuth();
  const [orders, setOrders] = useState<any[]>([]);
  const [fetching, setFetching] = useState(true);

  useEffect(() => {
    if (loading) return;
    if (!isAuthenticated || user?.user_type !== "admin") {
      router.push("/");
      return;
    }

    async function loadOrders() {
      try {
        const data = await getAdminOrders();
        setOrders(data.orders || []);
      } catch (error) {
        console.error(error);
      } finally {
        setFetching(false);
      }
    }

    loadOrders();
  }, [isAuthenticated, loading, router, user]);

  if (loading || fetching) {
    return <div className="p-10 text-center">Loading admin orders...</div>;
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

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-6xl mx-auto rounded-3xl bg-white p-8 shadow-xl">
        <h1 className="text-4xl font-bold mb-6">Admin Order Management</h1>
        {orders.length === 0 ? (
          <div className="text-center text-gray-500 py-16">No orders yet.</div>
        ) : (
          <div className="space-y-6">
            {orders.map((order) => (
              <div key={order.order_id} className="border rounded-3xl p-6 shadow-sm">
                <div className="flex flex-col md:flex-row justify-between gap-4 mb-4">
                  <div className="flex items-center gap-4">
                    {order.restaurant?.image ? (
                      <img
                        src={order.restaurant.image}
                        alt={order.restaurant.name || "Restaurant"}
                        className="h-16 w-16 rounded-3xl object-cover"
                      />
                    ) : (
                      <div className="h-16 w-16 rounded-3xl bg-gray-200" />
                    )}
                    <div>
                      <div className="text-xl font-bold">Order #{order.order_id}</div>
                      <div className="text-gray-500">{order.restaurant?.name || order.restaurant_id}</div>
                    </div>
                  </div>
                  <div className="flex flex-col items-start md:items-end gap-2">
                    <span className={`px-3 py-1 rounded-full font-semibold ${statusClasses[order.status] || "bg-gray-100 text-gray-800"}`}>
                      {statusLabel[order.status] || order.status}
                    </span>
                    <div className="text-orange-500 font-bold text-xl">₹{order.total_amount}</div>
                  </div>
                </div>

                <div className="grid gap-2 text-sm text-gray-600 mb-6">
                  <div>User: {order.user_id}</div>
                  <div>Payment: {order.payment_status}</div>
                  <div>Placed: {new Date(order.created_at).toLocaleString()}</div>
                </div>

                <div className="flex flex-wrap gap-3">
                  {['confirmed','preparing','ready','picked_up','on_the_way','delivered','cancelled'].map((status) => (
                    <button
                      key={status}
                      onClick={async () => {
                        try {
                          await updateOrderStatus(order.order_id, status);
                          setOrders((prev) => prev.map((o) => o.order_id === order.order_id ? { ...o, status } : o));
                        } catch (error) {
                          console.error(error);
                          alert('Failed to update order status.');
                        }
                      }}
                      className="bg-orange-500 text-white px-3 py-2 rounded-lg hover:bg-orange-600 transition"
                    >
                      {status.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
