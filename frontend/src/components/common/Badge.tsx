import React from 'react';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'identified' | 'weak' | 'unresolved' | 'neutral' | 'success';
  className?: string;
}

export function Badge({ children, variant = 'neutral', className = '' }: BadgeProps) {
  const variantStyles = {
    identified: 'bg-emerald-50 text-emerald-800 border-emerald-200',
    weak: 'bg-amber-50 text-amber-800 border-amber-200',
    unresolved: 'bg-rose-50 text-rose-800 border-rose-200',
    neutral: 'bg-slate-100 text-slate-700 border-slate-200',
    success: 'bg-blue-50 text-blue-800 border-blue-200',
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${variantStyles[variant]} ${className}`}
    >
      {children}
    </span>
  );
}
