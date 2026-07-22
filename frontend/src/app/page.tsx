import Footer from "@/components/Footer";
import Navbar from "@/components/Navbar";
import Catalog from "@/components/Catalog";

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen bg-[#f8fafc] font-sans text-slate-900 relative selection:bg-blue-100 selection:text-blue-900">
      
      {/* Navigation */}
      <Navbar />

      {/* Main Container */}
      <main className="flex-1 flex flex-col items-center z-10 w-full max-w-7xl mx-auto px-6 pt-6 pb-12">
        <Catalog />
      </main>
      
      <Footer />
    </div>
  );
}
