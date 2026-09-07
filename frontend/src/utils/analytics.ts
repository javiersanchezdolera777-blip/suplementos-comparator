export const trackEvent = (eventName: string, params?: Record<string, any>) => {
  if (typeof window !== 'undefined' && typeof window.gtag === 'function') {
    window.gtag('event', eventName, params);
  }
};

export const trackAffiliateClick = (productName: string, store: string, category: string) => {
  trackEvent('click_affiliate', {
    product_name: productName,
    store_name: store,
    product_category: category,
  });
};

export const trackViewItem = (productName: string, category: string) => {
  trackEvent('view_item', {
    product_name: productName,
    product_category: category,
  });
};

export const trackInteraction = (action: 'add_favorite' | 'remove_favorite' | 'add_compare' | 'remove_compare' | 'add_stack', productName: string) => {
  trackEvent('product_interaction', {
    interaction_type: action,
    product_name: productName,
  });
};

export const trackSearch = (searchQuery: string) => {
  if (!searchQuery.trim()) return;
  trackEvent('search_query', { search_term: searchQuery.toLowerCase() });
};

export const trackFilter = (filterType: string, filterValue: string) => {
  if (!filterValue || filterValue === 'Todas' || filterValue === 'Todos') return;
  trackEvent('filter_applied', { filter_type: filterType, filter_value: filterValue });
};
