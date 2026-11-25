import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CRM Oficina Pesados",
  description: "CRM para oficina de veículos de grande porte",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR">
      <body className="antialiased min-h-screen">{children}</body>
    </html>
  );
}
