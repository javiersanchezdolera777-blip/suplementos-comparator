"use client";

import React from 'react';

interface Props {
  href: string;
  productId: number;
  className?: string;
  children: React.ReactNode;
}

export default function TrackedAffiliateLink({ href, productId, className, children }: Props) {
  const trackClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
    // No bloqueamos la navegación normal (no hacemos e.preventDefault())
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    fetch(`${apiUrl}/api/click/${productId}`, { method: 'POST' }).catch(() => {});
  };

  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      onClick={trackClick}
      className={className}
    >
      {children}
    </a>
  );
}
