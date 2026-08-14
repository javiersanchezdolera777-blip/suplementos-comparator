import { MetadataRoute } from 'next'

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: 'Tus Suplementos',
    short_name: 'TusSuplementos',
    description: 'Compara precios y ahorra en tu suplementación',
    start_url: '/',
    display: 'standalone',
    background_color: '#f8fafc',
    theme_color: '#2563eb',
    icons: [
      {
        src: '/Logo_icon2.png',
        sizes: '192x192',
        type: 'image/png',
      },
      {
        src: '/Logo_icon2.png',
        sizes: '512x512',
        type: 'image/png',
      },
    ],
  }
}
