import { getRestaurant } from "@/lib/api";

export default async function RestaurantPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  // Next.js 16 Fix
  const { id } = await params;

  const restaurant = await getRestaurant(id);

  if (!restaurant) {
    return (
      <div className="p-10 text-2xl">
        Restaurant not found
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-gray-100 p-8">
      {/* Restaurant Header */}
      <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
        <img
          src="https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=1200&q=80"
          alt={restaurant.name}
          className="w-full h-80 object-cover"
        />

        <div className="p-8">
          <h1 className="text-5xl font-bold">
            {restaurant.name}
          </h1>

          <p className="text-xl text-gray-600 mt-4">
            {restaurant.cuisine.join(" • ")}
          </p>

          <div className="flex gap-8 mt-6 text-lg">
            <span>⭐ {restaurant.rating}</span>
            <span>🚚 {restaurant.delivery_time}</span>
          </div>

          <p className="mt-6 text-gray-700 text-lg">
            {restaurant.description}
          </p>
        </div>
      </div>

      {/* Menu Section */}
      <section className="mt-10">
        <h2 className="text-4xl font-bold mb-8">
          Menu
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {restaurant.menu.map((item: any) => (
            <div
              key={item.id}
              className="bg-white rounded-2xl shadow-lg p-6 hover:scale-105 transition"
            >
              <h3 className="text-2xl font-bold">
                {item.name}
              </h3>

              <p className="text-gray-600 mt-2">
                {item.description}
              </p>

              <div className="flex justify-between items-center mt-6">
                <span className="text-2xl font-bold text-orange-500">
                  ₹{item.price}
                </span>

                <button className="bg-orange-500 text-white px-4 py-2 rounded-xl hover:bg-orange-600 transition">
                  Add to Cart
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}