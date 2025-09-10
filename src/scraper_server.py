from flask import Flask, jsonify
from src.models.product import db
from src.scraper.myprotein_scraper import MyProteinScraper
from src.scraper.decathlon_scraper import DecathlonScraper
from src.utils.scheduler import schedule_scraping
import threading

def create_scraper_server():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///suplementos.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    @app.route('/api/scrape/all', methods=['POST'])
    def scrape_all():
        """Endpoint para ejecutar scraping manualmente"""
        try:
            scrapers = [MyProteinScraper(), DecathlonScraper()]
            results = {}
            
            for scraper in scrapers:
                with app.app_context():
                    results[scraper.store] = scraper.run_scraping()
            
            return jsonify({
                'status': 'success',
                'message': 'Scraping completado',
                'results': results
            })
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    @app.route('/api/scrape/status', methods=['GET'])
    def scrape_status():
        """Ver estado del scraping"""
        return jsonify({'status': 'running', 'last_update': '...'})
    
    return app

def run_scraper_server():
    """Ejecutar el servidor de scraping en puerto diferente"""
    scraper_app = create_scraper_server()
    
    # Iniciar scraping programado en segundo plano
    scheduler_thread = threading.Thread(target=schedule_scraping, daemon=True)
    scheduler_thread.start()
    
    scraper_app.run(debug=True, port=5001, use_reloader=False)

if __name__ == '__main__':
    run_scraper_server()