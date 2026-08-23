export const getWinnerMin = (products: any[], key: string) => {
  const validProducts = products.filter(p => p[key] !== null && p[key] !== undefined && p[key] > 0);
  if (validProducts.length === 0) return null;
  return Math.min(...validProducts.map(p => p[key]));
};

export const getWinnerMax = (products: any[], key: string) => {
  const validProducts = products.filter(p => p[key] !== null && p[key] !== undefined);
  if (validProducts.length === 0) return null;
  return Math.max(...validProducts.map(p => p[key]));
};
