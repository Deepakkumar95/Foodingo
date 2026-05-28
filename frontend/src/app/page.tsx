"use client";

import { useEffect, useState } from "react";
import { getRestaurants } from "@/lib/api";

interface Restaurant {
  id: string;
  name: string;
  cuisine: string;
  rating: number;
  delivery_time: string;
}

export default function Home() {
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchRestaurants() {
      try {
        const data = await getRestaurants();

        // Adjust based on your backend response
        setRestaurants(data.restaurants || []);
      } catch (error) {
        console.error("Error fetching restaurants:", error);
      } finally {
        setLoading(false);
      }
    }

    fetchRestaurants();
  }, []);

  return (
    <main className="min-h-screen bg-gray-100">
      {/* Navbar */}
      <nav className="bg-orange-500 text-white px-8 py-4 flex justify-between items-center">
        <h1 className="text-3xl font-bold">Foodingo</h1>

        <div className="flex gap-6 text-lg">
          <button>Home</button>
          <button>Orders</button>
          <button>Cart</button>
          <button>Login</button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="text-center py-16">
        <h2 className="text-5xl font-bold text-gray-800">
          Order Food Online
        </h2>

        <p className="mt-4 text-xl text-gray-600">
          Fast delivery from your favorite restaurants
        </p>

        <button className="mt-8 bg-orange-500 text-white px-6 py-3 rounded-xl text-lg hover:bg-orange-600">
          Explore Restaurants
        </button>
      </section>

      {/* Restaurant Section */}
      <section className="px-8 pb-16">
        <h3 className="text-3xl font-bold mb-8">
          Popular Restaurants
        </h3>

        {loading ? (
          <p>Loading restaurants...</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {restaurants.map((restaurant) => (
              <div
                key={restaurant.id}
                className="bg-white rounded-2xl shadow-lg overflow-hidden hover:scale-105 transition"
              >
                <div className="h-48 bg-gray-300"></div>

                <div className="p-4">
                  <h4 className="text-2xl font-bold">
                    {restaurant.name}
                  </h4>

                  <p className="text-gray-600">
                    {restaurant.cuisine}
                  </p>

                  <div className="flex justify-between mt-4">
                    <span>⭐ {restaurant.rating}</span>
                    <span>{restaurant.delivery_time}</span>
                  </div>

                  <button className="mt-4 w-full bg-orange-500 text-white py-2 rounded-xl hover:bg-orange-600">
                    View Menu
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}