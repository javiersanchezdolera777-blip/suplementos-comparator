import { NextResponse } from 'next/server';
import { generateSitemaps } from '../sitemap';

export async function GET() {
  // Llama a la misma función que ya tienes en sitemap.ts para saber cuántos chunks hay
  const sitemaps = await generateSitemaps();
  const baseUrl = 'https://www.tussuplementos.com';
  
  // Construye el XML estándar de sitemapindex
  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${sitemaps.map(s => `  <sitemap>
    <loc>${baseUrl}/sitemap/${s.id}.xml</loc>
  </sitemap>`).join('\n')}
</sitemapindex>`;

  // Devuelve la respuesta forzando el header XML
  return new NextResponse(xml, {
    headers: {
      'Content-Type': 'application/xml',
    },
  });
}
