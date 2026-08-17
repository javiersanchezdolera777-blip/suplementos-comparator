import Footer from "@/components/Footer";
import Navbar from "@/components/Navbar";
import Catalog from "@/components/Catalog";
import TelegramBanner from "@/components/TelegramBanner";
import NewsletterForm from "@/components/NewsletterForm";

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen bg-slate-50 font-sans text-slate-900 relative selection:bg-blue-100 selection:text-blue-900">
      
      {/* Announcement Bar at the very top */}
      <TelegramBanner/>
      
      {/* Navigation */}
      <Navbar/>

      {/* Main Container */}
      <main className="flex-1 flex flex-col items-center z-10 w-full max-w-7xl mx-auto px-6 pt-2 pb-12">
        <Catalog/>
        
        {/* Newsletter Section */}
        <div className="w-full mt-8">
          <NewsletterForm />
        </div>
      </main>
      
      <Footer/>
    </div>
  );
}
