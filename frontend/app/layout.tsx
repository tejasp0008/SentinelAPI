import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SentinelAPI — Zero-Trust Cybersecurity Dashboard",
  description:
    "Edge-adaptive, zero-trust cybersecurity platform. Continuously discovers APIs, analyzes security risks, and detects zombie APIs using machine learning.",
  keywords: [
    "cybersecurity",
    "API security",
    "zombie API",
    "zero-trust",
    "machine learning",
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="antialiased grid-bg">{children}</body>
    </html>
  );
}
