import Link from "next/link";

export default function SuccessPage() {
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-6">
      <div className="max-w-xl w-full rounded-3xl bg-white p-10 text-center shadow-xl">
        <div className="text-6xl">🎉</div>
        <h1 className="mt-6 text-4xl font-bold">Order Placed!</h1>
        <p className="mt-4 text-gray-600">
          Your delicious food is on the way.
        </p>
        <Link href="/" className="inline-block mt-8 bg-orange-500 text-white px-8 py-4 rounded-2xl hover:bg-orange-600 transition">
          Back to Home
        </Link>
      </div>
    </div>
  );
}
