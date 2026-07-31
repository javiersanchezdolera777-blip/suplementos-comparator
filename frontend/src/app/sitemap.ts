import { MetadataRoute } from 'next';

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const baseUrl = 'https://www.tussuplementos.com';
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  // 1. Rutas Estáticas Principales
  const staticRoutes: MetadataRoute.Sitemap = [
    {
      url: `${baseUrl}`,
      lastModified: new Date(),
      changeFrequency: 'daily',
      priority: 1.0,
    },
    {
      url: `${baseUrl}/#catalogo`,
      lastModified: new Date(),
      changeFrequency: 'daily',
      priority: 1.0,
    },
    {
      url: `${baseUrl}/about`,
      lastModified: new Date(),
      changeFrequency: 'monthly',
      priority: 0.5,
    },
    {
      url: `${baseUrl}/contact`,
      lastModified: new Date(),
      changeFrequency: 'monthly',
      priority: 0.5,
    },
    {
      url: `${baseUrl}/legal`,
      lastModified: new Date(),
      changeFrequency: 'yearly',
      priority: 0.3,
    },
    {
      url: `${baseUrl}/privacy`,
      lastModified: new Date(),
      changeFrequency: 'yearly',
      priority: 0.3,
    },
    {
      url: `${baseUrl}/cookies`,
      lastModified: new Date(),
      changeFrequency: 'yearly',
      priority: 0.3,
    },
  ];

  // 2. Rutas Dinámicas (Productos)
  let dynamicRoutes: MetadataRoute.Sitemap = [];
  try {
    // Solicitamos un límite holgado (hasta 5000 productos) para incluirlos todos.
    const res = await fetch(`${apiUrl}/api/productos?limit=5000`, { 
      // Usamos revalidación para no ahogar al backend en cada petición del sitemap
      next: { revalidate: 3600 } 
    });
    
    if (res.ok) {
      const data = await res.json();
      const productos = data.items || [];
      
      dynamicRoutes = productos.map((prod: any) => ({
        url: `${baseUrl}/producto/${prod.slug}`,
        lastModified: new Date(),
        changeFrequency: 'weekly',
        priority: 0.8,
      }));
    }
  } catch (error) {
    console.error("Error generando rutas dinámicas para el sitemap:", error);
  }

  return [...staticRoutes, ...dynamicRoutes];
}
