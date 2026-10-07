import { MetadataRoute } from 'next';

const baseUrl = 'https://www.tussuplementos.com';
const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const LIMIT = 5000;

export async function generateSitemaps() {
  try {
    // Fetch just the total count to calculate how many chunks we need
    const res = await fetch(`${apiUrl}/api/internal/sitemap-batch?offset=0&limit=1`, {
      next: { revalidate: 3600 }
    });
    if (!res.ok) return [{ id: 0 }];
    const data = await res.json();
    const total = data.total || 0;
    
    const chunks = Math.ceil(total / LIMIT);
    const sitemaps = [];
    for (let i = 0; i < (chunks || 1); i++) {
      sitemaps.push({ id: i });
    }
    return sitemaps;
  } catch (error) {
    return [{ id: 0 }];
  }
}

export default async function sitemap({ id }: { id: Promise<number> | number }): Promise<MetadataRoute.Sitemap> {
  const resolvedId = Number(await id);
  let routes: MetadataRoute.Sitemap = [];

  // Añadimos las rutas estáticas, categorías y marcas solo al primer sitemap (chunk 0)
  if (resolvedId === 0) {
    const staticRoutes: MetadataRoute.Sitemap = [
      { url: `${baseUrl}`, lastModified: new Date(), changeFrequency: 'daily', priority: 1.0 },
      { url: `${baseUrl}/#catalogo`, lastModified: new Date(), changeFrequency: 'daily', priority: 1.0 },
      { url: `${baseUrl}/about`, lastModified: new Date(), changeFrequency: 'monthly', priority: 0.5 },
      { url: `${baseUrl}/contact`, lastModified: new Date(), changeFrequency: 'monthly', priority: 0.5 },
      { url: `${baseUrl}/legal`, lastModified: new Date(), changeFrequency: 'yearly', priority: 0.3 },
      { url: `${baseUrl}/privacy`, lastModified: new Date(), changeFrequency: 'yearly', priority: 0.3 },
      { url: `${baseUrl}/cookies`, lastModified: new Date(), changeFrequency: 'yearly', priority: 0.3 },
    ];

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

    routes = [...staticRoutes, ...categoryRoutes, ...brandRoutes];
  }

  // Traer los productos correspondientes a este lote (chunk)
  const offset = resolvedId * LIMIT;
  try {
    const res = await fetch(`${apiUrl}/api/internal/sitemap-batch?offset=${offset}&limit=${LIMIT}`, {
      next: { revalidate: 3600 }
    });
    
    if (res.ok) {
      const data = await res.json();
      const productos = data.productos || [];
      
      const productRoutes: MetadataRoute.Sitemap = productos.map((prod: any) => ({
        url: `${baseUrl}/producto/${prod.slug}`,
        lastModified: new Date(),
        changeFrequency: 'daily',
        priority: 0.8,
      }));
      
      routes = [...routes, ...productRoutes];
    } else {
       console.error(`Sitemap fetch error en el chunk ${resolvedId}: status ${res.status}`);
    }
  } catch (error) {
    console.error(`Error crítico generando rutas dinámicas para el sitemap chunk ${resolvedId}:`, error);
  }

  return routes;
}
