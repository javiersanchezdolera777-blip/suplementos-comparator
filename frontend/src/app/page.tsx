import Footer from "@/components/Footer";
import Navbar from "@/components/Navbar";
import Catalog from "@/components/Catalog";
import TelegramBanner from "@/components/TelegramBanner";
import Link from 'next/link';

export default async function Home() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  
  let initialProducts = [];
  let initialTotal = 0;
  
  try {
    const res = await fetch(`${apiUrl}/api/productos?limit=36&page=1`, {
      next: { revalidate: 3600 } // ISR: revalida cada hora
    });
    if (res.ok) {
      const data = await res.json();
      initialProducts = data.productos || [];
      initialTotal = data.total_resultados || 0;
    }
  } catch (e) {
    console.error("Error fetching initial products for SSR:", e);
  }

  return (
    <div className="flex flex-col min-h-screen bg-slate-50 font-sans text-slate-900 relative selection:bg-blue-100 selection:text-blue-900">
      {/* Sticky Header Group: Banner + Navbar */}
      <header className="sticky top-0 z-50 flex flex-col w-full shadow-sm">
        {/* Announcement Bar at the very top */}
        <TelegramBanner/>
        
        {/* Navigation */}
        <Navbar/>
      </header>

      {/* Main Container */}
      <main className="flex-1 flex flex-col items-center z-10 w-full max-w-7xl mx-auto px-6 pt-2 pb-12">
        <Catalog initialProducts={initialProducts} initialTotal={initialTotal} />
      </main>
      
      <Footer/>
    </div>
  );
}
