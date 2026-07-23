import { Metadata } from 'next';
import { notFound } from 'next/navigation';
import Link from 'next/link';

interface Props {
  params: Promise<{ slug: string }>;
}

const decodeHTML = (str: string) => {
  if (!str) return "";
  return str
    .replace(/&#8211;/g, "–")
    .replace(/&#8212;/g, "—")
    .replace(/&amp;/g, "&")
    .replace(/&#8217;/g, "'")
    .replace(/&quot;/g, '"')
    .replace(/&#039;/g, "'")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">");
};

async function getProduct(slug: string) {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  try {
    const res = await fetch(`${apiUrl}/api/productos/slug/${slug}`, {
      cache: 'no-store'
    });

    if (!res.ok) {
      return null;
    }

    return await res.json();
  } catch (error) {
    console.error("Error cargando producto por slug:", error);
    return null;
  }
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const product = await getProduct(slug);

  if (!product) {
    return {
      title: 'Producto no encontrado | Suparator',
      description: 'El suplemento solicitado no está disponible en Suparator.'
    };
  }

  const cleanName = decodeHTML(product.name);
  const cleanDescription = product.description
    ? decodeHTML(product.description).slice(0, 150)
    : `Compara precios y especificaciones de ${cleanName} en tiendas oficiales.`;

  const title = `${cleanName} - Mejor Precio | Suparator`;
  const description = `Compara precios y especificaciones de ${cleanName} en tiendas oficiales. ${cleanDescription}...`;

  return {
    title,
    description,
    openGraph: {
      title,
      description,
      images: product.image_url ? [{ url: product.image_url }] : [],
      type: 'website',
    },
    twitter: {
      card: 'summary_large_image',
      title,
      description,
      images: product.image_url ? [product.image_url] : [],
    }
  };
}

export default async function ProductDetailPage({ params }: Props) {
  const { slug } = await params;
  const product = await getProduct(slug);

  if (!product) {
    notFound();
  }

  const cleanName = decodeHTML(product.name);
  const hasImage = product.image_url && product.image_url.trim() !== "";
  const categoryName = product.category?.name || "Suplementos";
  const brandName = product.brand?.name || "Sin marca";
  const proteinPercent = product.protein_percentage ?? product.porcentaje_proteina;

  return (
    <div className="min-h-screen bg-slate-50/50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto">
        
        {/* 1. NAVEGACIÓN Y BREADCRUMB */}
        <div className="flex items-center justify-between gap-4 mb-6 text-sm">
          <nav className="flex items-center gap-2 text-slate-500 font-medium overflow-x-auto py-1">
            <Link href="/" className="hover:text-blue-600 transition-colors">
              Inicio
            </Link>
            <span>/</span>
            <span className="text-slate-600 font-semibold">{categoryName}</span>
            <span>/</span>
            <span className="text-slate-900 font-bold truncate max-w-[200px] sm:max-w-xs">{cleanName}</span>
          </nav>
        </div>

        {/* 2. TARJETA PRINCIPAL DEL PRODUCTO */}
        <div className="bg-white border border-slate-200 rounded-3xl shadow-sm overflow-hidden grid grid-cols-1 lg:grid-cols-12 gap-0">
          
          {/* COLUMNA IZQUIERDA: IMAGEN Y BADGES */}
          <div className="lg:col-span-5 bg-slate-50 p-8 sm:p-12 flex flex-col items-center justify-center border-b lg:border-b-0 lg:border-r border-slate-100 relative min-h-[380px]">
            {/* Badges superiores */}
            <div className="absolute top-6 left-6 flex flex-wrap gap-2">
              {proteinPercent && (
                <span className="bg-blue-600 text-white font-black text-xs px-3 py-1.5 rounded-xl shadow-sm">
                  {proteinPercent}% Proteína
                </span>
              )}
              {product.quality_seal && (
                <span className="bg-blue-50 text-blue-700 border border-blue-200 font-bold text-xs px-3 py-1.5 rounded-xl">
                  {product.quality_seal}
                </span>
              )}
              {product.is_vegan && (
                <span className="bg-emerald-50 text-emerald-700 border border-emerald-200 font-bold text-xs px-3 py-1.5 rounded-xl">
                  🌱 Vegano
                </span>
              )}
            </div>

            {hasImage ? (
              <img
                src={product.image_url}
                alt={cleanName}
                className="w-full h-auto max-h-[380px] object-contain drop-shadow-md transition-transform duration-300 hover:scale-105"
              />
            ) : (
              <div className="flex flex-col items-center justify-center text-slate-300">
                <span className="font-black tracking-[0.3em] text-2xl uppercase">Suparator</span>
                <span className="text-xs font-medium mt-2">Imagen no disponible</span>
              </div>
            )}
          </div>

          {/* COLUMNA DERECHA: INFORMACIÓN DETALLADA */}
          <div className="lg:col-span-7 p-6 sm:p-10 flex flex-col justify-between">
            <div>
              {/* Marca */}
              <div className="text-xs font-bold tracking-widest text-slate-400 uppercase mb-2">
                {brandName}
              </div>

              {/* Título */}
              <h1 className="text-2xl sm:text-4xl font-black text-slate-900 mb-4 leading-tight">
                {cleanName}
              </h1>

              {/* Bloque de Precio */}
              <div className="flex items-baseline gap-2 mb-6">
                <span className="text-slate-400 text-sm font-bold">Desde</span>
                <span className="text-3xl sm:text-4xl font-black text-blue-600">
                  {product.price?.toFixed(2)}€
                </span>
              </div>

              {/* Descripción */}
              {product.description && (
                <div className="mb-8 bg-slate-50/70 p-4 sm:p-5 rounded-2xl border border-slate-100">
                  <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Descripción del producto</h2>
                  <p className="text-slate-600 text-sm leading-relaxed whitespace-pre-line">
                    {decodeHTML(product.description)}
                  </p>
                </div>
              )}

              {/* TABLA TÉCNICA DE ESPECIFICACIONES */}
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mb-8 bg-slate-50 p-5 rounded-2xl border border-slate-100 text-sm">
                <div className="flex flex-col">
                  <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Categoría</span>
                  <span className="text-slate-800 font-bold mt-0.5">{categoryName}</span>
                </div>

                <div className="flex flex-col">
                  <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Formato</span>
                  <span className="text-slate-800 font-bold mt-0.5">{product.format || '-'}</span>
                </div>

                <div className="flex flex-col">
                  <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Sabores</span>
                  <span className="text-slate-800 font-bold mt-0.5">
                    {Array.isArray(product.flavor)
                      ? (product.flavor.length ? product.flavor.join(', ') : '-')
                      : (product.flavor ? String(product.flavor) : '-')}
                  </span>
                </div>

                {product.protein_type && (
                  <div className="flex flex-col">
                    <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Tipo de Proteína</span>
                    <span className="text-slate-800 font-bold mt-0.5">{product.protein_type}</span>
                  </div>
                )}

                {product.creatine_type && (
                  <div className="flex flex-col">
                    <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Tipo de Creatina</span>
                    <span className="text-slate-800 font-bold mt-0.5">{product.creatine_type}</span>
                  </div>
                )}

                {product.amino_profile && (
                  <div className="flex flex-col">
                    <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Perfil Aminoácidos</span>
                    <span className="text-slate-800 font-bold mt-0.5">{product.amino_profile}</span>
                  </div>
                )}

                {product.vitamin_type && (
                  <div className="flex flex-col">
                    <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Tipo Vitamina</span>
                    <span className="text-slate-800 font-bold mt-0.5">{product.vitamin_type}</span>
                  </div>
                )}
              </div>
            </div>

            {/* BOTÓN CTA COMPRA AFILIADO */}
            <div className="pt-4 border-t border-slate-100">
              <a
                href={product.affiliate_url || "#"}
                target="_blank"
                rel="noopener noreferrer"
                className="w-full flex items-center justify-center gap-3 py-4 px-6 bg-blue-600 hover:bg-blue-700 text-white rounded-2xl font-bold text-base transition-all shadow-lg shadow-blue-600/25 active:scale-98 cursor-pointer"
              >
                <span>Ver oferta en la tienda oficial</span>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
