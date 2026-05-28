const API_BASE_URL =
  "https://musical-doodle-v6vxrrg9pgwc6wq9-8000.app.github.dev";

export async function getRestaurants() {
  try {
    const response = await fetch(
      `${API_BASE_URL}/restaurants`,
      {
        headers: {
          Accept: "application/json",
        },
        cache: "no-store",
      }
    );

    if (!response.ok) {
      throw new Error("Failed to fetch restaurants");
    }

    return await response.json();
  } catch (error) {
    console.error("API ERROR:", error);
    return [];
  }
}

export async function getRestaurant(id: string) {
  try {
    const restaurants = await getRestaurants();

    return restaurants.find(
      (restaurant: any) =>
        restaurant.restaurant_id === id
    );
  } catch (error) {
    console.error("Restaurant Error:", error);
    return null;
  }
}