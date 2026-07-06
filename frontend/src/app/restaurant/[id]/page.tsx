import { getRestaurant } from "@/lib/api";
import AddToCartButton from "@/components/AddToCartButton";
import RestaurantImage from "@/components/RestaurantImage";
import { CartProduct } from "@/context/CartContext";

const FOOD_FALLBACK_IMAGES: Record<string, string> = {
  paneer:
    "https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?auto=format&fit=crop&w=900&q=80",
  tikka:
    "https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?auto=format&fit=crop&w=900&q=80",
  naan:
    "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?auto=format&fit=crop&w=900&q=80",
  bread:
    "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?auto=format&fit=crop&w=900&q=80",
  pizza:
    "https://images.unsplash.com/photo-1550547660-d9450f859349?auto=format&fit=crop&w=900&q=80",
  garlic:
    "https://images.unsplash.com/photo-1498654896293-37aacf113fd9?auto=format&fit=crop&w=900&q=80",
  cheese:
    "https://images.unsplash.com/photo-1498654896293-37aacf113fd9?auto=format&fit=crop&w=900&q=80",
  burger:
    "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?auto=format&fit=crop&w=900&q=80",
  salad:
    "https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?auto=format&fit=crop&w=900&q=80",
  sushi:
    "https://images.unsplash.com/photo-1550547660-d9450f859349?auto=format&fit=crop&w=900&q=80",
  default:
    "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=900&q=80",
};

function getMenuItemFallbackImage(name: string) {
  const lowerName = name.toLowerCase();

  for (const key of Object.keys(FOOD_FALLBACK_IMAGES)) {
    if (key !== "default" && lowerName.includes(key)) {
      return FOOD_FALLBACK_IMAGES[key];
    }
  }

  return FOOD_FALLBACK_IMAGES.default;
}

export default async function RestaurantPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const restaurant = await getRestaurant(id);

  if (!restaurant) {
    return (
      <div className="p-10 text-2xl">
        Restaurant not found.
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-gray-100 p-4 md:p-8 md:pr-96">
      <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
        <RestaurantImage
          src={restaurant.image}
          alt={restaurant.name}
          className="w-full h-80 object-cover"
        />

        <div className="p-8">
          <h1 className="text-5xl font-bold">
            {restaurant.name}
          </h1>

          <p className="text-xl text-gray-600 mt-4">
            {restaurant.cuisine?.join(" • ")}
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

      <section className="mt-10">
        <h2 className="text-4xl font-bold mb-8">Menu</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {restaurant.menu.map((item: CartProduct & { description?: string; image?: string }) => (
            <div
              key={item.id}
              className="bg-white rounded-2xl shadow-lg overflow-hidden hover:scale-105 transition"
            >
              <RestaurantImage
                src={item.image}
                alt={item.name}
                fallbackSrc={getMenuItemFallbackImage(item.name)}
                className="h-40 w-full object-cover"
              />

              <div className="p-6">
                <h3 className="text-2xl font-bold">{item.name}</h3>
                <p className="text-gray-600 mt-2">{item.description}</p>

                <div className="flex justify-between items-center mt-6">
                  <span className="text-2xl font-bold text-orange-500">
                    ₹{item.price}
                  </span>
                  <AddToCartButton
                    item={{
                      ...item,
                      restaurant_id:
                        restaurant.restaurant_id,
                    }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}