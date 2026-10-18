import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
  hoverable?: boolean;
}

export function Card({ children, className = '', onClick, hoverable = false }: CardProps) {
  return (
    <div
      onClick={onClick}
      className={`bg-white rounded-2xl border border-slate-200/80 shadow-[0_4px_20px_-4px_rgba(15,23,42,0.05)] transition-all ${
        hoverable ? 'cursor-pointer hover:border-slate-300 hover:shadow-[0_10px_30px_-8px_rgba(37,99,235,0.12)]' : ''
      } ${className}`}
    >
      {children}
    </div>
  );
}
