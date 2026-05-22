import { useMemo } from 'react';
import { StockHistoryItem, PredictionData } from '../../types';

export function PriceTower({ history, prediction }: { history: StockHistoryItem[]; prediction: PredictionData | null }) {
  const bars = useMemo(() => {
    const slice = history.slice(-30);
    const max = Math.max(...slice.map((d) => d.high), prediction?.predicted_price ?? 1, 1);
    const min = Math.min(...slice.map((d) => d.low), prediction?.predicted_price ?? 1);
    return slice.map((d, i) => ({ x: (i - slice.length / 2) * 0.13, height: 0.18 + ((d.close - min) / Math.max(max - min, 1)) * 1.6, up: d.close >= d.open }));
  }, [history, prediction]);
  return (
    <group position={[2.9, -1.45, -1.2]} rotation={[0, -0.35, 0]}>
      {bars.map((bar, index) => (
        <mesh key={index} position={[bar.x, bar.height / 2, 0]}>
          <boxGeometry args={[0.075, bar.height, 0.24]} />
          <meshStandardMaterial color={bar.up ? '#22c55e' : '#ef4444'} emissive={bar.up ? '#064e3b' : '#7f1d1d'} emissiveIntensity={0.8} transparent opacity={0.8} />
        </mesh>
      ))}
      {prediction && <mesh position={[2.14, 0.95, 0]}><boxGeometry args={[0.1, 1.9, 0.28]} /><meshStandardMaterial color="#c084fc" emissive="#7e22ce" emissiveIntensity={1.2} transparent opacity={0.45} /></mesh>}
    </group>
  );
}
