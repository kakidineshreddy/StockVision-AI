import { formatDistanceToNow } from 'date-fns';

export const formatCurrency = (value: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 2 }).format(Number.isFinite(value) ? value : 0);
export const formatPercent = (value: number) => `${value >= 0 ? '+' : ''}${(Number.isFinite(value) ? value : 0).toFixed(2)}%`;
export const compactNumber = (value: number) => new Intl.NumberFormat('en-US', { notation: 'compact', maximumFractionDigits: 1 }).format(Number.isFinite(value) ? value : 0);
export const relativeTime = (value: string) => {
  try { return formatDistanceToNow(new Date(value), { addSuffix: true }); } catch { return 'just now'; }
};
