import { MetadataRoute } from 'next';
import { notFound } from 'next/navigation';

const baseUrl = 'https://www.tussuplementos.com';
const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const LIMIT = 1000;

type SitemapBatchResponse = {
  total: number;
  productos: { slug: string }[];
};

function isValidBatchResponse(data: unknown): data is SitemapBatchResponse {
  if (typeof data !== 'object' || data === null) return false;
  const { total, productos } = data as Record<string, unknown>;
  if (typeof total !== 'number' || !Number.isInteger(total) || total < 0) return false;
  if (!Array.isArray(productos)) return false;
  return productos.every(
    (p) =>
      typeof p === 'object' &&
      p !== null &&
      typeof (p as Record<string, unknown>).slug === 'string' &&
      ((p as Record<string, unknown>).slug as string).trim() !== ''
  );
}

// Obtiene un lote del backend. Si falla la red, el status o el formato, registra el
// error y lo propaga: es preferible un error controlado a un sitemap incompleto.
async function fetchSitemapBatch(offset: number, limit: number): Promise<SitemapBatchResponse> {
  const url = `${apiUrl}/api/internal/sitemap-batch?offset=${offset}&limit=${limit}`;

  let res: Response;
  try {
    res = await fetch(url, { next: { revalidate: 3600 } });
  } catch (error) {
    console.error(`[sitemap] Error de red al consultar ${url}:`, error);
    throw new Error(`[sitemap] No se pudo conectar con el backend (offset=${offset})`);
  }

  if (!res.ok) {
    console.error(`[sitemap] Respuesta no válida del backend en ${url}: status ${res.status}`);
    throw new Error(`[sitemap] El backend respondió con status ${res.status} (offset=${offset})`);
  }

  let data: unknown;
  try {
    data = await res.json();
  } catch (error) {
    console.error(`[sitemap] JSON inválido en ${url}:`, error);
    throw new Error(`[sitemap] Respuesta JSON inválida del backend (offset=${offset})`);
  }

  if (!isValidBatchResponse(data)) {
    console.error(`[sitemap] Formato de respuesta inesperado en ${url}`);
    throw new Error(`[sitemap] Formato de respuesta inesperado del backend (offset=${offset})`);
  }

  return data;
}

export async function generateSitemaps() {
  // Solo necesitamos el total de productos elegibles para calcular los lotes
  const { total } = await fetchSitemapBatch(0, 1);

  // Siempre existe al menos el lote 0 (rutas estáticas), aunque no haya productos
  const chunks = Math.max(1, Math.ceil(total / LIMIT));
  return Array.from({ length: chunks }, (_, i) => ({ id: i }));
}

export default async function sitemap(props: { id: Promise<string> }): Promise<MetadataRoute.Sitemap> {
  const rawId = await props.id;
  const resolvedId = Number(rawId);

  if (!/^\d+$/.test(String(rawId)) || !Number.isSafeInteger(resolvedId) || resolvedId < 0) {
    notFound();
  }

  let routes: MetadataRoute.Sitemap = [];

  // Añadimos las rutas estáticas, categorías y marcas solo al primer sitemap (chunk 0)
  if (resolvedId === 0) {
    const staticRoutes: MetadataRoute.Sitemap = [
      { url: `${baseUrl}`, changeFrequency: 'daily', priority: 1.0 },
      { url: `${baseUrl}/about`, changeFrequency: 'monthly', priority: 0.5 },
      { url: `${baseUrl}/contact`, changeFrequency: 'monthly', priority: 0.5 },
      { url: `${baseUrl}/legal`, changeFrequency: 'yearly', priority: 0.3 },
      { url: `${baseUrl}/privacy`, changeFrequency: 'yearly', priority: 0.3 },
      { url: `${baseUrl}/cookies`, changeFrequency: 'yearly', priority: 0.3 },
    ];

    const categorias = ['proteinas', 'creatinas', 'vitaminas', 'aminoacidos', 'pre-entrenos'];
    const marcas = ['hsn', 'myprotein', 'optimum-nutrition', 'zumub', 'amix', 'prozis', 'scitec'];

    const categoryRoutes: MetadataRoute.Sitemap = categorias.map((cat) => ({
      url: `${baseUrl}/categoria/${cat}`,
      changeFrequency: 'daily',
      priority: 0.9,
    }));

    const brandRoutes: MetadataRoute.Sitemap = marcas.map((marca) => ({
      url: `${baseUrl}/marca/${marca}`,
      changeFrequency: 'daily',
      priority: 0.9,
    }));

    routes = [...staticRoutes, ...categoryRoutes, ...brandRoutes];
  }

  // Traer los productos correspondientes a este lote (chunk). Los errores se propagan.
  const offset = resolvedId * LIMIT;
  const { total, productos } = await fetchSitemapBatch(offset, LIMIT);

  // Un lote > 0 fuera de rango no debe servirse como sitemap vacío
  if (resolvedId > 0 && offset >= total) {
    notFound();
  }

  // Defensa ante duplicados dentro del lote (el slug es único en BD)
  const slugsUnicos = Array.from(new Set(productos.map((p) => p.slug)));

  const productRoutes: MetadataRoute.Sitemap = slugsUnicos.map((slug) => ({
    url: `${baseUrl}/producto/${slug}`,
    changeFrequency: 'daily',
    priority: 0.8,
  }));

  return [...routes, ...productRoutes];
}
