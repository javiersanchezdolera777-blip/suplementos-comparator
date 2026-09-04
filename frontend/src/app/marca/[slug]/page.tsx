import { Metadata } from 'next';
import { notFound } from 'next/navigation';
import Catalog from '@/components/Catalog';
import Footer from "@/components/Footer";
import Navbar from "@/components/Navbar";
import TelegramBanner from "@/components/TelegramBanner";

interface Props {
  params: Promise<{ slug: string }>;
}

const cleanBrandSlug = (slug: string): string => {
  const map: Record<string, string> = {
    'hsn': 'HSN',
    'farma2go': 'Farma2Go',
    'pharma2go': 'Farma2Go',
    'myprotein': 'MyProtein',
    'optimum-nutrition': 'Optimum Nutrition',
    'zumub': 'Zumub',
    'amix': 'Amix',
    'prozis': 'Prozis',
    'scitec': 'Scitec',
  };
  
  if (map[slug.toLowerCase()]) {
    return map[slug.toLowerCase()];
  }
  
  return slug
    .split('-')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const brandName = cleanBrandSlug(slug);
  return {
    title: `Suplementos ${brandName} Baratos - Mejores Ofertas 2026 | Tus Suplementos`,
    description: `Compara precios de todo el catálogo de ${brandName}. Encuentra las mejores ofertas y ahorra en tus suplementos deportivos.`,
    alternates: {
      canonical: `https://www.tussuplementos.com/marca/${slug}`,
    }
  };
}

export default async function BrandPage({ params }: Props) {
  const { slug } = await params;
  const brandName = cleanBrandSlug(slug);
  
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  let initialProducts = [];
  let initialTotal = 0;

  try {
    const res = await fetch(`${apiUrl}/api/productos?marcas=${encodeURIComponent(brandName)}&limit=36`, {
      next: { revalidate: 3600 }
    });
    
    if (res.ok) {
      const data = await res.json();
      initialProducts = data.productos || [];
      initialTotal = data.total_resultados || 0;
    }
  } catch (error) {
    console.error("Error fetching brand products:", error);
  }

  return (
    <div className="flex flex-col min-h-screen bg-slate-50 font-sans text-slate-900 relative selection:bg-blue-100 selection:text-blue-900">
      <header className="sticky top-0 z-50 flex flex-col w-full shadow-sm">
        <TelegramBanner/>
        <Navbar/>
      </header>

      <main className="flex-1 flex flex-col items-center z-10 w-full max-w-7xl mx-auto px-6 pt-2 pb-12">
        <Catalog 
          initialProducts={initialProducts} 
          initialTotal={initialTotal} 
          preselectedBrand={brandName} 
        />
      </main>
      
      <Footer/>
    </div>
  );
}
