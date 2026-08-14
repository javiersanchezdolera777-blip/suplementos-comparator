import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { GoogleAnalytics } from '@next/third-parties/google';
import Script from 'next/script';
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
  icons: {
    icon: [
      { url: '/Logo_icon2.png?v=2', sizes: 'any' },
      { url: '/icon.png?v=2', type: 'image/png' },
    ],
    shortcut: '/Logo_icon2.png?v=2',
    apple: [
      { url: '/apple-icon.png?v=2', sizes: '180x180', type: 'image/png' },
    ],
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
      data-scroll-behavior="smooth"
      suppressHydrationWarning
    >
      <head>
        <link rel="icon" href="/Logo_icon2.png?v=3" type="image/png" sizes="any" />
        <link rel="shortcut icon" href="/Logo_icon2.png?v=3" type="image/png" />
        <link rel="apple-touch-icon" href="/Logo_icon2.png?v=3" />
      </head>
      <body className="min-h-full flex flex-col max-w-full overflow-x-hidden bg-slate-50 text-slate-900" suppressHydrationWarning>
        <Providers>
          {children}
        </Providers>
        <GoogleAnalytics gaId={process.env.NEXT_PUBLIC_GA_ID || "G-GMZDENG5MM"} />
        <Script
          id="tradetracker-verification"
          strategy="afterInteractive"
          dangerouslySetInnerHTML={{
            __html: `
              var _TradeTrackerTagOptions = {
                  t: 'a',
                  s: '513818',
                  chk: 'c75ecefc6f1b74c3facb15579341e058',
                  overrideOptions: {}
              };

              (function() {var tt = document.createElement('script'), s = document.getElementsByTagName('script')[0]; tt.setAttribute('type', 'text/javascript'); tt.setAttribute('src', (document.location.protocol == 'https:' ? 'https' : 'http') + '://tm.tradetracker.net/tag?t=' + _TradeTrackerTagOptions.t + '&s=' + _TradeTrackerTagOptions.s + '&chk=' + _TradeTrackerTagOptions.chk); s.parentNode.insertBefore(tt, s);})();
            `
          }}
        />
      </body>
    </html>
  );
}
