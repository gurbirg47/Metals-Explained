import type { Metadata } from "next";
import "./globals.css";
import Navigation from "@/components/Navigation";

export const metadata: Metadata = {
  title: "Metals, Explained",
  description: "A learning-focused dashboard for understanding gold and silver markets",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Navigation />
        <main className="px-6 py-6 max-w-7xl mx-auto">
          {children}
        </main>
        <footer className="text-center mono text-sm text-[var(--text-muted)] mt-12 py-6 border-t border-[rgba(255,255,255,0.1)]">
          <p className="mb-2">DATA: YAHOO FINANCE | MANUAL REFRESH | FOR LEARNING ONLY | NOT INVESTMENT ADVICE</p>
          <p className="font-['Bitter']">
            Created by Gurbir Gill<br />
            <span className="text-xs">Accounting & Finance student with an interest in Sales & Trading and market structure.</span>
          </p>
        </footer>
      </body>
    </html>
  );
}
