import Link from "next/link";
import { getRestaurants } from "@/lib/api";

export default async function Home() {
  const restaurants = await getRestaurants();

  return (
    <main className="min-h-screen bg-gray-100">
      {/* Navbar */}
      <nav className="bg-orange-500 text-white px-8 py-4 flex justify-between items-center">
        <h1 className="text-3xl font-bold">
          Foodingo
        </h1>

        <div className="flex gap-6 text-lg">
          <button>Home</button>
          <button>Orders</button>
          <button>Cart</button>
          <button>Login</button>
        </div>
      </nav>

      {/* Hero */}
      <section className="text-center py-16">
        <h2 className="text-5xl font-bold text-gray-800">
          Order Food Online
        </h2>

        <p className="mt-4 text-xl text-gray-600">
          Fast delivery from your favorite restaurants
        </p>

        <button className="mt-8 bg-orange-500 text-white px-6 py-3 rounded-xl text-lg">
          Explore Restaurants
        </button>
      </section>

      {/* Restaurants */}
      <section className="px-8 pb-16">
        <h3 className="text-3xl font-bold mb-8">
          Popular Restaurants
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {restaurants.map((restaurant: any) => (
            <Link
              key={restaurant.id}
              href={`/restaurant/${restaurant.restaurant_id}`}
            >
              <div className="bg-white rounded-2xl shadow-lg overflow-hidden hover:scale-105 transition">
                <img
                  src="https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=900&q=80"
                  alt={restaurant.name}
                  className="h-48 w-full object-cover"
                />

                <div className="p-4">
                  <h4 className="text-2xl font-bold">
                    {restaurant.name}
                  </h4>

                  <p className="text-gray-600">
                    {restaurant.cuisine.join(" • ")}
                  </p>

                  <div className="flex justify-between mt-4">
                    <span>
                      ⭐ {restaurant.rating}
                    </span>

                    <span>
                      {restaurant.delivery_time}
                    </span>
                  </div>

                  <button className="mt-4 w-full bg-orange-500 text-white py-2 rounded-xl">
                    View Menu
                  </button>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </section>
    </main>
  );
}