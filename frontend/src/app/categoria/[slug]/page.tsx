import { Metadata } from 'next';
import { notFound } from 'next/navigation';
import Catalog from '@/components/Catalog';
import Footer from "@/components/Footer";
import Navbar from "@/components/Navbar";
import TelegramBanner from "@/components/TelegramBanner";

interface Props {
  params: Promise<{ slug: string }>;
}

const mapCategorySlug = (slug: string): string => {
  const map: Record<string, string> = {
    'proteina': 'Proteínas',
    'proteinas': 'Proteínas',
    'creatina': 'Creatinas',
    'creatinas': 'Creatinas',
    'vitaminas': 'Vitaminas y Minerales',
    'minerales': 'Vitaminas y Minerales',
    'aminoacidos': 'Aminoácidos',
    'pre-entreno': 'Pre-entrenos',
    'pre-entrenos': 'Pre-entrenos',
  };
  return map[slug.toLowerCase()] || slug.charAt(0).toUpperCase() + slug.slice(1).replace(/-/g, ' ');
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const categoryName = mapCategorySlug(slug);
  return {
    title: `Comprar ${categoryName} al Mejor Precio - Comparativa 2026 | Tus Suplementos`,
    description: `Descubre los mejores precios en ${categoryName}. Compara ofertas de HSN, Farma2Go, Amazon y más en Tus Suplementos.`,
    alternates: {
      canonical: `https://www.tussuplementos.com/categoria/${slug}`,
    }
  };
}

export default async function CategoryPage({ params }: Props) {
  const { slug } = await params;
  const categoryName = mapCategorySlug(slug);
  
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  let initialProducts = [];
  let initialTotal = 0;

  try {
    const res = await fetch(`${apiUrl}/api/productos?categoria=${encodeURIComponent(categoryName)}&limit=36`, {
      next: { revalidate: 3600 }
    });
    
    if (res.ok) {
      const data = await res.json();
      initialProducts = data.productos || [];
      initialTotal = data.total_resultados || 0;
    }
  } catch (error) {
    console.error("Error fetching category products:", error);
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
          preselectedCategory={categoryName} 
        />
      </main>
      
      <Footer/>
    </div>
  );
}
