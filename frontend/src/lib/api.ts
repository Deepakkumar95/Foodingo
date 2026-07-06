const API_BASE_URL =
  process.env.API_BASE_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "http://localhost:8000";

const ENDPOINTS = {
  RESTAURANTS: `${API_BASE_URL}/restaurants`,
  // use frontend proxy routes for auth so browser requests don't hit cross-origin
  SIGNUP: `/api/auth/signup`,
  LOGIN: `/api/auth/login`,
  USERS_ME: `/api/users/me`,
  ORDERS: `/api/orders`,
};


// GET ALL RESTAURANTS
export async function getRestaurants() {
  try {
    const response = await fetch(ENDPOINTS.RESTAURANTS);

    if (!response.ok) {
      const text = await response.text();
      console.error(
        "API ERROR: Failed to fetch restaurants",
        response.status,
        text
      );
      return [];
    }

    const clone = response.clone();
    try {
      return await response.json();
    } catch (jsonError) {
      const text = await clone.text();
      console.error(
        "API ERROR: Invalid restaurant JSON response",
        text
      );
      return [];
    }
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
        restaurant.restaurant_id === id || restaurant.id === id
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
    const response = await fetch(ENDPOINTS.SIGNUP, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(text || "Signup failed");
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
    const response = await fetch(ENDPOINTS.LOGIN, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      throw new Error("Login failed");
    }

    return await response.json();
  } catch (error) {
    console.error("LOGIN ERROR:", error);

    throw error;
  }
}

export async function fetchCurrentUser(token?: string) {
  try {
    const authToken = token || localStorage.getItem("token");
    if (!authToken) {
      throw new Error("Missing authentication token");
    }

    const response = await fetch(ENDPOINTS.USERS_ME, {
      headers: {
        Authorization: `Bearer ${authToken}`,
      },
    });

    if (!response.ok) {
      throw new Error("Failed to fetch user profile");
    }

    return await response.json();
  } catch (error) {
    console.error("USER FETCH ERROR:", error);
    throw error;
  }
}

export async function fetchOrders(token?: string) {
  try {
    const authToken = token || localStorage.getItem("token");
    if (!authToken) {
      throw new Error("Missing authentication token");
    }

    const response = await fetch(ENDPOINTS.ORDERS, {
      headers: {
        Authorization: `Bearer ${authToken}`,
      },
    });

    if (!response.ok) {
      throw new Error("Failed to fetch orders");
    }

    return await response.json();
  } catch (error) {
    console.error("ORDER FETCH ERROR:", error);
    throw error;
  }
}

// PLACE ORDER
export async function placeOrder(
  orderData: any,
  token: string
) {
  try {
    const response = await fetch(ENDPOINTS.ORDERS, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(orderData),
    });

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