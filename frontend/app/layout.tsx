import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "CareerGraph",
  description: "AI job-search analyst",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <div className="app-shell">
          <header className="app-header">
            <div className="brand-block">
              <span className="brand-kicker">CareerGraph</span>
              <p className="brand-copy">A grounded job-search analyst for profile-first matching.</p>
            </div>
            <nav className="app-nav">
              <Link href="/">Dashboard</Link>
              <Link href="/profile">Profile</Link>
            </nav>
          </header>
          {children}
        </div>
      </body>
    </html>
  );
}
