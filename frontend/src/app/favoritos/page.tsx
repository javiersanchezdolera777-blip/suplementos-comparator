"use client";

import { useEffect, useState } from "react";
import { useAuth } from "../../context/AuthContext";
import ProductCard from "../../components/ProductCard";
import Navbar from "../../components/Navbar";
import Footer from "../../components/Footer";

export default function FavoritosPage() {
  const { isLoggedIn, token, openLoginModal } = useAuth();
  const [favoritos, setFavoritos] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Si no está logueado, no intentamos hacer fetch
    if (!isLoggedIn) {
      setLoading(false);
      return;
    }

    const fetchFavoritos = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const res = await fetch(`${apiUrl}/api/favoritos`, {
          headers: {
            "Authorization": `Bearer ${token}`
          }
        });
        
        if (res.ok) {
          const data = await res.json();
          setFavoritos(data);
        }
      } catch (error) {
        console.error("Error cargando favoritos:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchFavoritos();
  }, [isLoggedIn, token]);

  return (
    <div className="min-h-screen bg-[#030712] text-slate-300 font-sans selection:bg-blue-500/30 flex flex-col">
      <Navbar />

      <main className="flex-grow max-w-7xl mx-auto w-full px-6 py-12 md:py-20">
        <div className="mb-12">
          <h1 className="text-4xl md:text-5xl font-black text-white mb-4 tracking-tight">Mis Favoritos</h1>
          <p className="text-slate-400 text-lg max-w-2xl">
            Tus suplementos guardados para hacer seguimiento de sus precios.
          </p>
        </div>

        {!isLoggedIn ? (
          // Estado: No logueado
          <div className="bg-white/[0.02] border border-white/5 rounded-3xl p-12 text-center flex flex-col items-center">
            <div className="w-20 h-20 bg-blue-500/10 rounded-full flex items-center justify-center mb-6">
              <svg className="w-10 h-10 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-white mb-4">Inicia sesión para ver tus favoritos</h2>
            <p className="text-slate-400 mb-8 max-w-md">
              Guarda los suplementos que más te interesan y vuelve a ellos en cualquier momento con un solo clic.
            </p>
            <button 
              onClick={openLoginModal}
              className="px-8 py-3 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl transition-all shadow-lg shadow-blue-600/20"
            >
              Iniciar Sesión
            </button>
          </div>
        ) : loading ? (
          // Estado: Cargando
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 mt-8">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="flex flex-col bg-[#0a0f1d]/50 border border-white/5 rounded-3xl overflow-hidden h-[420px] animate-pulse">
                <div className="h-[220px] bg-white/5"></div>
                <div className="p-6 flex flex-col flex-grow">
                  <div className="h-3 w-1/4 bg-white/5 rounded mb-3"></div>
                  <div className="h-6 w-3/4 bg-white/10 rounded mb-4"></div>
                  <div className="h-4 w-full bg-white/5 rounded mb-2"></div>
                  <div className="h-4 w-5/6 bg-white/5 rounded mb-8"></div>
                </div>
              </div>
            ))}
          </div>
        ) : favoritos.length > 0 ? (
          // Estado: Con Favoritos
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {favoritos.map((fav) => (
              // Pasamos la flag isFavoriteActive a ProductCard si es necesario,
              // o asumimos que en esta vista todos son favoritos.
              <ProductCard key={fav.product_id} product={fav.product} />
            ))}
          </div>
        ) : (
          // Estado: Vacío
          <div className="bg-white/[0.02] border border-white/5 rounded-3xl p-12 text-center flex flex-col items-center">
            <div className="w-20 h-20 bg-slate-800/50 rounded-full flex items-center justify-center mb-6">
              <svg className="w-10 h-10 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-white mb-4">Aún no tienes favoritos</h2>
            <p className="text-slate-400 mb-8 max-w-md">
              Explora nuestro catálogo y marca el corazón de los suplementos que quieras tener controlados.
            </p>
            <a 
              href="/#catalogo"
              className="px-8 py-3 bg-white text-black font-bold rounded-xl transition-all shadow-lg hover:bg-slate-200"
            >
              Explorar Catálogo
            </a>
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
}
