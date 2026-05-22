export const clamp = (value: number, min: number, max: number) => Math.min(max, Math.max(min, value));
export const sentimentColor = (score: number) => score > 0.2 ? '#22c55e' : score < -0.2 ? '#ef4444' : '#eab308';
export const signalColor = (signal?: string) => signal === 'BUY' ? 'emerald' : signal === 'SELL' ? 'rose' : 'amber';
