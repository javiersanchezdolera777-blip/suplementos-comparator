// Variables globales para la comparación
let comparisonProducts = [];

document.addEventListener('DOMContentLoaded', function() {
    console.log("Página cargada correctamente");
    
    // Configurar event listeners para todos los filtros
    const filterSelects = document.querySelectorAll('.form-select');
    filterSelects.forEach(select => {
        select.addEventListener('change', applyFilters);
    });
    
    // Cargar comparación guardada al iniciar
    loadComparisonFromStorage();
    
    // Configurar botones de comparar (ahora usan onclick en el HTML)
    // Los botones ya no necesitan event listeners aquí porque usan onclick
});

function applyFilters() {
    const category = document.getElementById('categoryFilter').value;
    const objetivo = document.getElementById('objetivoFilter').value;
    const caracteristicas = document.getElementById('caracteristicasFilter').value;
    const priceRange = document.getElementById('priceFilter').value;
    
    let minPrice = 0;
    let maxPrice = 1000;
    
    if (priceRange) {
        if (priceRange === '100+') {
            minPrice = 100;
            maxPrice = 10000;
        } else {
            const [min, max] = priceRange.split('-');
            minPrice = parseInt(min);
            maxPrice = parseInt(max);
        }
    }
    
    console.log('Aplicando filtros:', { 
        category, 
        objetivo, 
        caracteristicas, 
        minPrice, 
        maxPrice 
    });
    
    // Enviar filtros al servidor
    filterProducts(category, objetivo, caracteristicas, minPrice, maxPrice);
}

function filterProducts(category, objetivo, caracteristicas, minPrice, maxPrice) {
    // Construir URL con parámetros
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (objetivo) params.append('objetivo', objetivo);
    if (caracteristicas) params.append('caracteristicas', caracteristicas);
    params.append('min_price', minPrice);
    params.append('max_price', maxPrice);
    
    // Recargar la página con los filtros aplicados
    window.location.href = `/productos?${params.toString()}`;
}

// ==============================================
// SISTEMA DE COMPARACIÓN (FUNCIONES NUEVAS)
// ==============================================

function addToComparison(button) {
    const productId = button.getAttribute('data-product-id');
    const productName = button.getAttribute('data-product-name');
    const productPrice = button.getAttribute('data-product-price');
    const productImage = button.getAttribute('data-product-image');
    const productBrand = button.getAttribute('data-product-brand');
    const productCategory = button.getAttribute('data-product-category');
    
    // Verificar si ya está en comparación
    if (comparisonProducts.find(p => p.id === productId)) {
        showNotification('Este producto ya está en comparación', 'warning');
        return;
    }
    
    // Límite de 4 productos
    if (comparisonProducts.length >= 4) {
        showNotification('Máximo 4 productos para comparar', 'warning');
        return;
    }
    
    // Añadir a la comparación
    comparisonProducts.push({
        id: productId,
        name: productName,
        price: productPrice,
        image: productImage,
        brand: productBrand,
        category: productCategory
    });
    
    // Actualizar UI y guardar en localStorage
    updateComparisonUI();
    saveComparisonToStorage();
    showNotification(`"${productName}" añadido a comparación`, 'success');
    
    // Efecto visual en el botón
    button.classList.add('btn-success');
    button.innerHTML = '<i class="fas fa-check"></i> Añadido';
    setTimeout(() => {
        button.classList.remove('btn-success');
        button.innerHTML = '<i class="fas fa-balance-scale"></i> Comparar';
    }, 2000);
}

// Actualizar la barra de comparación
function updateComparisonUI() {
    const countElement = document.getElementById('comparison-count');
    const namesElement = document.getElementById('comparison-names');
    const comparisonBar = document.querySelector('.comparison-bar');
    
    if (countElement && namesElement && comparisonBar) {
        countElement.textContent = comparisonProducts.length;
        namesElement.textContent = comparisonProducts.map(p => p.name).join(', ');
        
        // Mostrar/ocultar barra
        comparisonBar.style.display = comparisonProducts.length > 0 ? 'block' : 'none';
    }
}

// Limpiar comparación
function clearComparison() {
    comparisonProducts = [];
    updateComparisonUI();
    localStorage.removeItem('product_comparison');
    showNotification('Comparación limpiada', 'info');
}

// Guardar en localStorage
function saveComparisonToStorage() {
    localStorage.setItem('product_comparison', JSON.stringify(comparisonProducts));
}

// Cargar desde localStorage al iniciar
function loadComparisonFromStorage() {
    const saved = localStorage.getItem('product_comparison');
    if (saved) {
        comparisonProducts = JSON.parse(saved);
        updateComparisonUI();
    }
}

// Abrir página de comparación
function openComparison() {
    if (comparisonProducts.length < 2) {
        showNotification('Selecciona al menos 2 productos para comparar', 'warning');
        return;
    }
    
    // Redirigir a página de comparación
    const productIds = comparisonProducts.map(p => p.id).join('-');
    window.location.href = `/comparar?products=${productIds}`;
}
    
// ==============================================
// FUNCIONES EXISTENTES (MANTENIDAS)
// ==============================================

function showNotification(message, type = 'info') {
    // Crear notificación bonita
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 1050; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-eliminar después de 3 segundos
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 3000);
}

// Función para cargar opciones de filtros dinámicamente (opcional)
async function loadFilterOptions() {
    try {
        const response = await fetch('/api/filtros');
        const options = await response.json();
        
        // Aquí podrías popularar selects dinámicamente
        console.log('Opciones de filtros:', options);
    } catch (error) {
        console.error('Error cargando opciones de filtros:', error);
    }
}

// Función anterior (ahora reemplazada por la nueva addToComparison)
// La mantengo por si acaso, pero ya no se usa
function addToComparisonOld(productId, productName) {
    console.log(`Añadiendo producto ${productName} (ID: ${productId}) a comparación`);
    showNotification(`"${productName}" añadido para comparar`, 'success');
}