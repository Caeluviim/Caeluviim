import type { Metadata, Viewport } from "next";
import { headers } from "next/headers";
import "./globals.css";

export async function generateMetadata(): Promise<Metadata> {
  const requestHeaders = await headers();
  const host = requestHeaders.get("x-forwarded-host") ?? requestHeaders.get("host") ?? "localhost:3000";
  const forwardedProtocol = requestHeaders.get("x-forwarded-proto")?.split(",")[0]?.trim();
  const protocol = forwardedProtocol ?? (host.startsWith("localhost") || host.startsWith("127.") ? "http" : "https");
  const origin = `${protocol}://${host}`;
  const socialImage = new URL("/og.png", origin).toString();
  const description =
    "A phone-ready source-bound knowledge graph that AI platforms query through MCP to produce fully mapped, provenance-explicit response tables.";

  return {
    title: "Caeluviim — Graph/Table Response Protocol",
    description,
    applicationName: "Caeluviim Protocol",
    manifest: "/manifest.webmanifest",
    openGraph: {
      title: "Caeluviim Graph/Table Protocol",
      description,
      type: "website",
      images: [{ url: socialImage, width: 1662, height: 946, alt: "Caeluviim graph flowing into a structured response table" }],
    },
    twitter: {
      card: "summary_large_image",
      title: "Caeluviim Graph/Table Protocol",
      description,
      images: [socialImage],
    },
  };
}

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
  themeColor: "#0b0e0d",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
