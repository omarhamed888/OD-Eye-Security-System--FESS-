'use client';

import { usePathname } from 'next/navigation';
import Navbar from '../components/Navbar';
import "./globals.css";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const pathname = usePathname();
  const isLoginPage = pathname === '/login';

  return (
    <html lang="en">
      <body className="antialiased bg-background text-foreground min-h-screen">
        {!isLoginPage && <Navbar />}
        <main>{children}</main>
      </body>
    </html>
  );
}
