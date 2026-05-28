"use client";

import { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { loginUser } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");

    try {
      const data = await loginUser(email, password);
      login(data.access_token);
      router.push("/");
    } catch (err: any) {
      setError(err?.message || "Login failed");
    }
  }

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-6">
      <div className="max-w-md w-full rounded-3xl bg-white p-8 shadow-xl">
        <h1 className="text-4xl font-bold mb-6">Login</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-semibold mb-2">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full border rounded-2xl px-4 py-3 outline-none"
              placeholder="you@example.com"
            />
          </div>
          <div>
            <label className="block text-sm font-semibold mb-2">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full border rounded-2xl px-4 py-3 outline-none"
              placeholder="Enter your password"
            />
          </div>
          {error ? <div className="text-red-500">{error}</div> : null}
          <button
            type="submit"
            className="w-full bg-orange-500 text-white py-3 rounded-2xl hover:bg-orange-600 transition"
          >
            Login
          </button>
        </form>
        <p className="mt-6 text-center text-gray-600">
          New here?{' '}
          <Link href="/signup" className="text-orange-500 font-semibold">
            Create an account
          </Link>
        </p>
      </div>
    </div>
  );
}
