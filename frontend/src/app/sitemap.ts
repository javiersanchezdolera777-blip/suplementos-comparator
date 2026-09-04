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

  // 1.5. Rutas Dinámicas (Categorías y Marcas)
  const categorias = ['proteinas', 'creatinas', 'vitaminas', 'aminoacidos', 'pre-entrenos'];
  const marcas = ['hsn', 'farma2go', 'myprotein', 'optimum-nutrition', 'zumub', 'amix', 'prozis', 'scitec'];

  const categoryRoutes: MetadataRoute.Sitemap = categorias.map((cat) => ({
    url: `${baseUrl}/categoria/${cat}`,
    lastModified: new Date(),
    changeFrequency: 'daily',
    priority: 0.9,
  }));

  const brandRoutes: MetadataRoute.Sitemap = marcas.map((marca) => ({
    url: `${baseUrl}/marca/${marca}`,
    lastModified: new Date(),
    changeFrequency: 'daily',
    priority: 0.9,
  }));

  // 2. Rutas Dinámicas (Productos)
  let dynamicRoutes: MetadataRoute.Sitemap = [];
  try {
    let allProducts: any[] = [];
    let hasMore = true;
    let page = 1;
    const limit = 200;

    while (hasMore) {
      try {
        const res = await fetch(`${apiUrl}/api/productos?limit=${limit}&page=${page}`, { 
          next: { revalidate: 3600 } 
        });
        
        if (!res.ok) {
          console.error(`Sitemap fetch error en la página ${page}: status ${res.status}`);
          break; // Stop fetching on error, but keep accumulated products
        }

        const data = await res.json();
        const productos = data.productos || [];
        
        if (productos.length > 0) {
          allProducts = [...allProducts, ...productos];
        }

        // If we received fewer products than the limit, we've reached the end
        if (productos.length < limit) {
          hasMore = false;
        } else {
          page++;
        }
      } catch (err) {
        console.error(`Sitemap network error en la página ${page}:`, err);
        break; // Stop fetching on network error
      }
    }
      
    dynamicRoutes = allProducts.map((prod: any) => ({
      url: `${baseUrl}/producto/${prod.slug}`,
      lastModified: new Date(),
      changeFrequency: 'daily',
      priority: 0.8,
    }));
  } catch (error) {
    console.error("Error crítico generando rutas dinámicas para el sitemap:", error);
  }

  return [...staticRoutes, ...categoryRoutes, ...brandRoutes, ...dynamicRoutes];
}
