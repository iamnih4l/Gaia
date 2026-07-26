import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { QueryProvider } from "@/providers/QueryProvider";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Gaia — Climate Intelligence & Tipping Point Prediction",
  description: "Research-grade AI platform for early detection of climate tipping points (AMOC, Amazon Dieback, Greenland, Antarctic Ice Sheets, Coral Reefs). Powered by Transformers, GNNs, PINNs, and Causal AI.",
  keywords: ["Climate AI", "Tipping Points", "AMOC", "Amazon Dieback", "PINN", "GNN", "Next.js", "DeepMind", "NASA"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`dark ${inter.variable} ${jetbrainsMono.variable} h-full antialiased`}
      style={{ colorScheme: "dark" }}
    >
      <body className="min-h-full bg-[#070C1B] text-[#F8F9FA] flex flex-col font-sans selection:bg-cyan-500/30 selection:text-cyan-200">
        <QueryProvider>{children}</QueryProvider>
      </body>
    </html>
  );
}
