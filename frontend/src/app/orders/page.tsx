"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { fetchOrders } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";

export default function OrdersPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  const [orders, setOrders] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
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
        setLoading(false);
      }
    }

    loadOrders();
  }, [isAuthenticated, router]);

  if (loading) {
    return <div className="p-10 text-center">Loading orders...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-5xl mx-auto rounded-3xl bg-white p-8 shadow-xl">
        <h1 className="text-4xl font-bold mb-6">Your Orders</h1>
        {orders.length === 0 ? (
          <div className="text-center text-gray-500 py-16">
            No orders yet.
          </div>
        ) : (
          <div className="space-y-4">
            {orders.map((order) => (
              <div key={order.order_id} className="border rounded-3xl p-6">
                <div className="flex justify-between items-center mb-4">
                  <div>
                    <div className="font-bold text-xl">Order #{order.order_id}</div>
                    <div className="text-gray-500">Status: {order.status}</div>
                  </div>
                  <div className="text-orange-500 font-bold">₹{order.total_amount}</div>
                </div>
                <div className="grid gap-2 text-sm text-gray-600">
                  <div>Restaurant: {order.restaurant_id}</div>
                  <div>Payment: {order.payment_status}</div>
                  <div>Placed: {new Date(order.created_at).toLocaleString()}</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
