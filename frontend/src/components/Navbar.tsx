"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";

export default function Navbar() {
  const router = useRouter();
  const { isAuthenticated, logout, user, loading } = useAuth();

  return (
    <nav className="bg-orange-500 text-white px-8 py-4 flex flex-col md:flex-row md:items-center gap-4 md:gap-0 justify-between">
      <div className="flex items-center gap-6">
        <Link href="/" className="text-2xl font-bold">Foodingo</Link>
        <button
          onClick={() => router.push("/#restaurants")}
          className="text-lg hover:underline"
        >
          Explore Restaurants
        </button>
      </div>

      <div className="flex flex-col md:flex-row items-center gap-4 text-lg">
        <Link href="/orders">Orders</Link>
        <Link href="/checkout">Cart</Link>
        {loading ? null : isAuthenticated ? (
          <div className="flex flex-wrap items-center gap-3">
            <Link href="/profile" className="text-white hover:underline">
              Profile
            </Link>
            {user?.user_type === "admin" ? (
              <Link href="/admin" className="bg-white text-orange-500 px-3 py-1 rounded-full font-semibold hover:bg-orange-100 transition">
                Admin
              </Link>
            ) : null}
            <span className="bg-white text-orange-500 px-3 py-1 rounded-full font-semibold">
              {user?.name || "User"}
            </span>
            <button
              onClick={() => {
                logout();
                router.push("/login");
              }}
              className="bg-white text-orange-500 px-4 py-2 rounded-full font-semibold hover:bg-orange-100 transition"
            >
              Logout
            </button>
          </div>
        ) : (
          <>
            <Link href="/login">Login</Link>
            <Link href="/signup">Signup</Link>
          </>
        )}
      </div>
    </nav>
  );
}
