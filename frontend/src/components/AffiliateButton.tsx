"use client";

import { trackAffiliateClick } from '@/utils/analytics';

interface Props {
  href: string;
  className?: string;
  productName: string;
  storeName: string;
  categoryName: string;
  children: React.ReactNode;
}

export default function AffiliateButton({ href, className, productName, storeName, categoryName, children }: Props) {
  return (
    <a
      href={href}
      target="_blank"
      rel="nofollow noopener noreferrer"
      className={className}
      onClick={() => trackAffiliateClick(productName, storeName, categoryName)}
    >
      {children}
    </a>
  );
}
