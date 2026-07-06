import "./globals.css";

import { AuthProvider } from "@/context/AuthContext";
import { CartProvider } from "@/context/CartContext";
import CartSidebar from "@/components/CartSidebar";
import Navbar from "@/components/Navbar";

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
              <div className="flex-1">
                <Navbar />
                {children}
              </div>
              <CartSidebar />
            </div>
          </CartProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
