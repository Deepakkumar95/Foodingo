"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";

export default function Navbar() {
  const router = useRouter();
  const { isAuthenticated, logout } = useAuth();

  return (
    <nav className="bg-orange-500 text-white px-8 py-4 flex justify-between items-center">
      <div className="flex items-center gap-6">
        <Link href="/" className="text-2xl font-bold">Foodingo</Link>
        <button
          onClick={() => router.push("/#restaurants")}
          className="text-lg hover:underline"
        >
          Explore Restaurants
        </button>
      </div>

      <div className="flex gap-6 text-lg">
        <Link href="/orders">Orders</Link>
        <Link href="/checkout">Cart</Link>
        {isAuthenticated ? (
          <button
            onClick={() => {
              logout();
              router.push("/");
            }}
          >
            Logout
          </button>
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
