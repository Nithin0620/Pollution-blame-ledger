import { UncertaintyRange } from '../types';

export const WHO_24H_GUIDELINE = 15.0;

export function formatNumber(val: number, decimals: number = 0): string {
  if (isNaN(val) || val === null || val === undefined) return '-';
  return val.toLocaleString('en-IN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

export function formatPercent(val: number): string {
  if (isNaN(val) || val === null || val === undefined) return '0%';
  return `${Math.round(val * 100)}%`;
}

export function formatRange(range: UncertaintyRange, decimals: number = 0): string {
  if (!range) return '-';
  return `${formatNumber(range.lo, decimals)} – ${formatNumber(range.hi, decimals)}`;
}
