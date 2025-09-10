import schedule
import time
from src.scraper.myprotein_scraper import MyProteinScraper
from src.scraper.decathlon_scraper import DecathlonScraper
from src.models.product import db
from src.app import create_app

def run_scraping_job():
    """Tarea programada para ejecutar scraping"""
    app = create_app()
    
    with app.app_context():
        scrapers = [MyProteinScraper(), DecathlonScraper()]
        
        for scraper in scrapers:
            try:
                print(f"Ejecutando scraping programado para {scraper.store}...")
                scraper.run_scraping()
                print(f"Scraping completado para {scraper.store}")
            except Exception as e:
                print(f"Error en scraping de {scraper.store}: {e}")

def schedule_scraping():
    """Programar tareas de scraping"""
    # Ejecutar cada 6 horas
    schedule.every(6).hours.do(run_scraping_job)
    
    # Ejecutar inmediatamente al iniciar
    run_scraping_job()
    
    print("Scraping programado iniciado. Ejecutando cada 6 horas.")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Revisar cada minuto