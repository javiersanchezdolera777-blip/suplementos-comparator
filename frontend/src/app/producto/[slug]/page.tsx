import { Metadata } from 'next';
import { notFound } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';
import TrackedAffiliateLink from '@/components/TrackedAffiliateLink';
import ProductViewTracker from '@/components/ProductViewTracker';

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
      next: { revalidate: 3600 }
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
      title: 'Producto no encontrado | Tus Suplementos',
      description: 'El suplemento solicitado no está disponible en Tus Suplementos.'
    };
  }

  const cleanName = decodeHTML(product.name);
  const cleanDescription = product.description
    ? decodeHTML(product.description).slice(0, 150)
    : `Compara precios y especificaciones de ${cleanName} en tiendas oficiales.`;

  const price = product.price ? product.price.toFixed(2) : "0.00";
  const title = `${cleanName} desde ${price}€ - Mejor Precio | Tus Suplementos`;
  const description = `Compara precios y especificaciones de ${cleanName} en tiendas oficiales. Encuéntralo hoy desde ${price}€. ${cleanDescription}...`;
  const url = `https://www.tussuplementos.com/producto/${slug}`;

  return {
    title,
    description,
    alternates: {
      canonical: url,
    },
    openGraph: {
      title,
      description,
      url,
      siteName: 'Tus Suplementos',
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

  let offersSchema: any = {
    "@type": "AggregateOffer",
    "url": `https://www.tussuplementos.com/producto/${slug}`,
    "priceCurrency": "EUR",
    "lowPrice": product.price || 0,
    "highPrice": product.price || 0,
    "offerCount": 1
  };

  if (product.ofertas && product.ofertas.length > 0) {
    const activeOffers = product.ofertas.filter((o: any) => o.activo);
    if (activeOffers.length > 0) {
      const prices = activeOffers.map((o: any) => o.precio);
      offersSchema = {
        "@type": "AggregateOffer",
        "url": `https://www.tussuplementos.com/producto/${slug}`,
        "priceCurrency": "EUR",
        "lowPrice": Math.min(...prices),
        "highPrice": Math.max(...prices),
        "offerCount": activeOffers.length,
        "offers": activeOffers.map((o: any) => ({
          "@type": "Offer",
          "price": o.precio,
          "priceCurrency": "EUR",
          "seller": { "@type": "Organization", "name": o.tienda },
          "url": `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/out/${o.tienda.toLowerCase()}/${product.slug}`
        }))
      };
    }
  }

  const jsonLd = {
    "@context": "https://schema.org/",
    "@type": "Product",
    "name": cleanName,
    "image": product.image_url || "",
    "description": product.description ? decodeHTML(product.description).slice(0, 300) : `Compara precios de ${cleanName}`,
    "brand": {
      "@type": "Brand",
      "name": brandName
    },
    "offers": offersSchema
  };

  return (
    <div className="min-h-screen bg-slate-50/50 py-8 px-4 sm:px-6 lg:px-8">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <ProductViewTracker productId={product.id} />
      <div className="max-w-6xl mx-auto">

        {/* 1. NAVEGACIÓN Y BREADCRUMB */}
        <div className="flex items-center justify-between gap-4 mb-6 text-sm">
          <nav className="flex items-center gap-2 text-slate-500 font-medium overflow-x-auto py-1">
            <Link href="/" className="hover:text-blue-600 transition-colors">
              Inicio
            </Link>
            <span>/</span>
            <Link href={`/?categoria=${encodeURIComponent(categoryName)}`} className="text-slate-600 font-semibold hover:text-blue-600 transition-colors">
              {categoryName}
            </Link>
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
              <div className="relative w-full max-w-[350px] aspect-square mt-8 sm:mt-4">
                <Image
                  src={product.image_url}
                  alt={cleanName}
                  fill
                  priority
                  sizes="(max-width: 1024px) 100vw, 50vw"
                  className="object-contain drop-shadow-md transition-transform duration-300 hover:scale-105"
                />
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center text-slate-300">
                <span className="font-black tracking-[0.3em] text-2xl uppercase">Tus Suplementos</span>
                <span className="text-xs font-medium mt-2">Imagen no disponible</span>
              </div>
            )}
          </div>

          {/* COLUMNA DERECHA: INFORMACIÓN DETALLADA */}
          <div className="lg:col-span-7 p-6 sm:p-10 flex flex-col gap-8">
            <div>
              {/* Marca */}
              <div className="text-xs font-bold tracking-widest text-slate-400 uppercase mb-2">
                {brandName}
              </div>

              {/* Título */}
              <h1 className="text-2xl sm:text-4xl font-black text-slate-900 mb-4 leading-tight">
                {cleanName}
              </h1>

              {/* Bloque de Precio Minimalista */}
              <div className="flex items-center flex-wrap gap-3 mb-2">
                <span className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
                  {product.price?.toFixed(2)} €
                </span>

              </div>
            </div>

            {/* 1. TABLA MULTI-TIENDA (Compara y ahorra) */}
            <div>
              <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4">
                Compara y ahorra
              </h3>

              {product.ofertas && product.ofertas.filter((o: any) => o.activo).length > 0 ? (
                <div className="flex flex-col gap-3">
                  {product.ofertas
                    .filter((o: any) => o.activo)
                    .sort((a: any, b: any) => a.precio - b.precio)
                    .map((oferta: any, index: number) => (
                      <div
                        key={oferta.id}
                        className={`flex flex-col sm:flex-row items-start sm:items-center justify-between p-4 rounded-2xl border transition-all hover:shadow-md ${index === 0
                          ? "border-green-500 bg-green-50/50"
                          : "border-slate-200 bg-white"
                          }`}
                      >
                        <div className="flex flex-col mb-3 sm:mb-0">
                          <span className="font-extrabold text-slate-900 text-lg">{oferta.tienda}</span>

                        </div>

                        <div className="flex items-center w-full sm:w-auto justify-between sm:justify-end gap-5">
                          <div className="text-right flex flex-col items-end">
                            {oferta.precio_anterior && oferta.precio_anterior > oferta.precio && (
                              <span className="text-xs font-semibold line-through text-slate-400 mb-0.5">{oferta.precio_anterior.toFixed(2)} €</span>
                            )}
                            <span className={`text-2xl font-black tracking-tight ${index === 0 ? "text-green-700" : "text-slate-900"}`}>
                              {oferta.precio.toFixed(2)} €
                            </span>
                          </div>

                          <a
                            href={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/out/${oferta.tienda.toLowerCase()}/${product.slug}`}
                            target="_blank"
                            rel="nofollow noopener noreferrer"
                            className={`px-6 py-3 rounded-xl font-bold transition-all whitespace-nowrap ${index === 0 ? "bg-green-600 hover:bg-green-700 text-white shadow-lg shadow-green-600/20" : "bg-slate-900 hover:bg-slate-800 text-white"
                              }`}
                          >
                            Ver oferta
                          </a>
                        </div>
                      </div>
                    ))}
                </div>
              ) : (
                <div className="p-4 bg-red-50 text-red-600 rounded-xl border border-red-200 text-sm font-medium">
                  Actualmente no hay ofertas activas para este producto.
                </div>
              )}
            </div>

            {/* 2. TABLA TÉCNICA DE ESPECIFICACIONES */}
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 bg-slate-50 p-5 rounded-2xl border border-slate-100 text-sm">
              <div className="flex flex-col"><span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Categoría</span><span className="text-slate-800 font-bold mt-0.5">{categoryName}</span></div>
              <div className="flex flex-col"><span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Formato</span><span className="text-slate-800 font-bold mt-0.5">{product.format || '-'}</span></div>
              <div className="flex flex-col"><span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Sabores</span><span className="text-slate-800 font-bold mt-0.5">{Array.isArray(product.flavor) ? (product.flavor.length ? product.flavor.join(', ') : '-') : (product.flavor ? String(product.flavor) : '-')}</span></div>
              {product.protein_type && <div className="flex flex-col"><span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Tipo de Proteína</span><span className="text-slate-800 font-bold mt-0.5">{product.protein_type}</span></div>}
              {product.creatine_type && <div className="flex flex-col"><span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Tipo de Creatina</span><span className="text-slate-800 font-bold mt-0.5">{product.creatine_type}</span></div>}
              {product.amino_profile && <div className="flex flex-col"><span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Perfil Aminoácidos</span><span className="text-slate-800 font-bold mt-0.5">{product.amino_profile}</span></div>}
              {product.vitamin_type && <div className="flex flex-col"><span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Tipo Vitamina</span><span className="text-slate-800 font-bold mt-0.5">{product.vitamin_type}</span></div>}
            </div>

            {/* 3. DESCRIPCIÓN CON TRUCO CSS "LEER MÁS" */}
            {product.description && (
              <div className="bg-slate-50/70 p-5 rounded-2xl border border-slate-100 relative group/desc">
                <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Descripción del producto</h2>

                <input type="checkbox" id="desc-toggle" className="peer hidden" />

                <p className="text-slate-600 text-sm leading-relaxed whitespace-pre-line line-clamp-4 peer-checked:line-clamp-none transition-all duration-300">
                  {decodeHTML(product.description)}
                </p>

                <label htmlFor="desc-toggle" className="text-blue-600 text-xs font-bold cursor-pointer mt-3 inline-block peer-checked:hidden hover:text-blue-800">
                  Leer más...
                </label>
                <label htmlFor="desc-toggle" className="text-blue-600 text-xs font-bold cursor-pointer mt-3 hidden peer-checked:inline-block hover:text-blue-800">
                  Leer menos
                </label>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}  