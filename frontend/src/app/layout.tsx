import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { GoogleAnalytics } from '@next/third-parties/google';
import "./globals.css";
import Providers from "./Providers";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Tus Suplementos | Comparador de Precios de Nutrición Deportiva",
  description: "Compara precios en tiempo real de proteínas, creatinas y vitaminas entre las mejores tiendas oficiales. Encuentra la mejor relación €/kg.",
  metadataBase: new URL('https://tussuplementos.es'),
  openGraph: {
    title: "Tus Suplementos | Comparador de Precios de Nutrición Deportiva",
    description: "Compara precios en tiempo real de proteínas, creatinas y vitaminas entre las mejores tiendas oficiales. Encuentra la mejor relación €/kg.",
    url: 'https://tussuplementos.es',
    siteName: 'Tus Suplementos',
    locale: 'es_ES',
    type: 'website',
    images: [
      {
        url: '/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'Tus Suplementos Comparador',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: "Tus Suplementos | Comparador de Precios de Nutrición Deportiva",
    description: "Compara precios en tiempo real de proteínas, creatinas y vitaminas entre las mejores tiendas oficiales. Encuentra la mejor relación €/kg.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="es"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased scroll-smooth`}
    >
      <body className="min-h-full flex flex-col max-w-full overflow-x-hidden" suppressHydrationWarning>
        <Providers>
          {children}
        </Providers>
        <GoogleAnalytics gaId={process.env.NEXT_PUBLIC_GA_ID || "G-GMZDENG5MM"} />
      </body>
    </html>
  );
}
