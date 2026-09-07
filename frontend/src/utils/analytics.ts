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
