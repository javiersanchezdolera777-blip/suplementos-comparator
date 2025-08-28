// Funcionalidad básica para demostración
document.addEventListener('DOMContentLoaded', function() {
    // Simular carga de productos
    console.log("Página cargada correctamente");
    
    // Ejemplo de funcionalidad de filtros
    const filterSelects = document.querySelectorAll('.form-select');
    filterSelects.forEach(select => {
        select.addEventListener('change', function() {
            console.log('Filtro aplicado:', this.value);
            // Aquí iría la lógica para filtrar productos
            applyFilters();
        });
    });
    
    // Funcionalidad de botones de comparar
    const compareButtons = document.querySelectorAll('.compare-btn');
    compareButtons.forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.getAttribute('data-product-id');
            const productCard = this.closest('.product-card');
            const productName = productCard.querySelector('h5').textContent;
            
            addToComparison(productId, productName);
        });
    });
});

function applyFilters() {
    // Lógica para aplicar filtros
    const category = document.getElementById('categoryFilter').value;
    const brand = document.getElementById('brandFilter').value;
    const price = document.getElementById('priceFilter').value;
    const rating = document.getElementById('ratingFilter').value;
    
    console.log('Aplicando filtros:', { category, brand, price, rating });
    
    // Aquí iría la lógica para filtrar los productos
    // Podría ser una llamada AJAX o un filtrado en el cliente
}

function addToComparison(productId, productName) {
    // Lógica para añadir producto a comparación
    console.log(`Añadiendo producto ${productName} (ID: ${productId}) a comparación`);
    
    // Mostrar mensaje de feedback
    alert(`Producto ${productName} añadido para comparar`);
    
    // Aquí iría la lógica para guardar en localStorage o enviar al backend
}