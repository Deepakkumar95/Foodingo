const API_BASE_URL =
  "https://potential-adventure-5gqwrr4jvrph459r-8000.app.github.dev";


// GET ALL RESTAURANTS
export async function getRestaurants() {
  try {
    const response = await fetch(
      `${API_BASE_URL}/restaurants`
    );

    if (!response.ok) {
      throw new Error(
        "Failed to fetch restaurants"
      );
    }

    return await response.json();
  } catch (error) {
    console.error("API ERROR:", error);

    return [];
  }
}


// GET SINGLE RESTAURANT
export async function getRestaurant(
  id: string
) {
  try {
    const restaurants =
      await getRestaurants();

    return restaurants.find(
      (restaurant: any) =>
        restaurant.id === id
    );
  } catch (error) {
    console.error("API ERROR:", error);

    return null;
  }
}


// SIGNUP USER
export async function signupUser(
  userData: {
    name: string;
    email: string;
    password: string;
  }
) {
  try {
    const response = await fetch(
      `${API_BASE_URL}/users/register`,
      {
        method: "POST",

        headers: {
          "Content-Type":
            "application/json",
        },

        body: JSON.stringify(userData),
      }
    );

    if (!response.ok) {
      throw new Error("Signup failed");
    }

    return await response.json();
  } catch (error) {
    console.error("SIGNUP ERROR:", error);

    throw error;
  }
}


// LOGIN USER
export async function loginUser(
  email: string,
  password: string
) {
  try {
    const formData =
      new URLSearchParams();

    formData.append(
      "username",
      email
    );

    formData.append(
      "password",
      password
    );

    const response = await fetch(
      `${API_BASE_URL}/token`,
      {
        method: "POST",

        headers: {
          "Content-Type":
            "application/x-www-form-urlencoded",
        },

        body: formData,
      }
    );

    if (!response.ok) {
      throw new Error("Login failed");
    }

    return await response.json();
  } catch (error) {
    console.error("LOGIN ERROR:", error);

    throw error;
  }
}


// PLACE ORDER
export async function placeOrder(
  orderData: any,
  token: string
) {
  try {
    const response = await fetch(
      `${API_BASE_URL}/orders`,
      {
        method: "POST",

        headers: {
          "Content-Type":
            "application/json",

          Authorization: `Bearer ${token}`,
        },

        body: JSON.stringify(orderData),
      }
    );

    if (!response.ok) {
      throw new Error(
        "Order placement failed"
      );
    }

    return await response.json();
  } catch (error) {
    console.error("ORDER ERROR:", error);

    throw error;
  }
}