import "./globals.css";

import { AuthProvider } from "@/context/AuthContext";
import { CartProvider } from "@/context/CartContext";
import CartSidebar from "@/components/CartSidebar";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <CartProvider>
            <div className="flex">
              <div className="flex-1">{children}</div>
              <CartSidebar />
            </div>
          </CartProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
