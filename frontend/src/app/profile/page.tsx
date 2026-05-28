"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { fetchCurrentUser } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";

export default function ProfilePage() {
  const router = useRouter();
  const { isAuthenticated, logout } = useAuth();
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login");
      return;
    }

    async function loadUser() {
      try {
        const data = await fetchCurrentUser();
        setUser(data.user);
      } catch (error) {
        logout();
        router.push("/login");
      } finally {
        setLoading(false);
      }
    }

    loadUser();
  }, [isAuthenticated, logout, router]);

  if (loading) {
    return <div className="p-10 text-center">Loading profile...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-3xl mx-auto rounded-3xl bg-white p-8 shadow-xl">
        <h1 className="text-4xl font-bold mb-6">Profile</h1>
        <div className="space-y-4 text-lg">
          <div>
            <span className="font-semibold">Name: </span>
            {user?.name}
          </div>
          <div>
            <span className="font-semibold">Email: </span>
            {user?.email}
          </div>
          <div>
            <span className="font-semibold">User type: </span>
            {user?.user_type}
          </div>
          <button
            onClick={() => {
              logout();
              router.push("/login");
            }}
            className="mt-6 bg-red-500 text-white px-6 py-3 rounded-2xl hover:bg-red-600 transition"
          >
            Logout
          </button>
        </div>
      </div>
    </div>
  );
}
