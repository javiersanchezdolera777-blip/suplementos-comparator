import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: 'hsnstore.com' },
      { protocol: 'https', hostname: '**.hsnstore.com' },
      { protocol: 'https', hostname: 'farma2go.es' },
      { protocol: 'https', hostname: '**.farma2go.es' },
      { protocol: 'https', hostname: 'sportlive.es' },
      { protocol: 'https', hostname: '**.sportlive.es' },
      { protocol: 'https', hostname: 'sportlivenutrition.com' },
      { protocol: 'https', hostname: '**.sportlivenutrition.com' },
      { protocol: 'https', hostname: 'amazon.es' },
      { protocol: 'https', hostname: '**.amazon.es' },
      { protocol: 'https', hostname: 'amazon.com' },
      { protocol: 'https', hostname: '**.amazon.com' },
      { protocol: 'https', hostname: 'tussuplementos.com' },
      { protocol: 'https', hostname: '**.tussuplementos.com' },
    ],
  },
};

export default nextConfig;
