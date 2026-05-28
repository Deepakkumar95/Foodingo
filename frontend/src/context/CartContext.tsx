"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
} from "react";

const CartContext = createContext<any>(null);

export function CartProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  // CART STATE
  const [cartItems, setCartItems] = useState<any[]>([]);

  // LOAD CART FROM LOCAL STORAGE
  useEffect(() => {
    const savedCart =
      localStorage.getItem("cart");

    if (savedCart) {
      setCartItems(JSON.parse(savedCart));
    }
  }, []);

  // SAVE CART TO LOCAL STORAGE
  useEffect(() => {
    localStorage.setItem(
      "cart",
      JSON.stringify(cartItems)
    );
  }, [cartItems]);

  // ADD TO CART
  function addToCart(item: any) {
    setCartItems((prev) => {
      const existingItem = prev.find(
        (cartItem) =>
          cartItem.id === item.id
      );

      // IF ITEM EXISTS → INCREASE QUANTITY
      if (existingItem) {
        return prev.map((cartItem) =>
          cartItem.id === item.id
            ? {
                ...cartItem,
                quantity:
                  cartItem.quantity + 1,
              }
            : cartItem
        );
      }

      // NEW ITEM
      return [
        ...prev,
        {
          ...item,
          quantity: 1,
        },
      ];
    });
  }

  // INCREASE QUANTITY
  function increaseQuantity(id: string) {
    setCartItems((prev) =>
      prev.map((item) =>
        item.id === id
          ? {
              ...item,
              quantity:
                item.quantity + 1,
            }
          : item
      )
    );
  }

  // DECREASE QUANTITY
  function decreaseQuantity(id: string) {
    setCartItems((prev) =>
      prev
        .map((item) =>
          item.id === id
            ? {
                ...item,
                quantity:
                  item.quantity - 1,
              }
            : item
        )
        .filter(
          (item) => item.quantity > 0
        )
    );
  }

  // REMOVE ITEM
  function removeFromCart(id: string) {
    setCartItems((prev) =>
      prev.filter(
        (item) => item.id !== id
      )
    );
  }

  return (
    <CartContext.Provider
      value={{
        cartItems,
        addToCart,
        increaseQuantity,
        decreaseQuantity,
        removeFromCart,
      }}
    >
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  return useContext(CartContext);
}