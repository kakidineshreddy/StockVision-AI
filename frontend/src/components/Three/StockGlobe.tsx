import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

const markers = [
  { ticker: 'AAPL', pos: [-0.9, 0.28, 0.72], color: '#22c55e' },
  { ticker: 'MSFT', pos: [-0.72, 0.42, 0.88], color: '#22c55e' },
  { ticker: 'TSLA', pos: [-0.98, 0.08, 0.48], color: '#eab308' },
  { ticker: 'NVDA', pos: [-0.82, 0.16, 0.9], color: '#22c55e' },
  { ticker: 'BABA', pos: [0.74, 0.18, 0.72], color: '#ef4444' },
  { ticker: 'BTC-USD', pos: [0.12, -0.28, 1.08], color: '#eab308' },
];

export function StockGlobe({ selectedTicker, onSelectTicker }: { selectedTicker: string; onSelectTicker: (ticker: string) => void }) {
  const group = useRef<THREE.Group>(null);
  useFrame((_, delta) => { if (group.current) group.current.rotation.y += delta * 0.12; });
  return (
    <group ref={group} position={[-3.3, 0.2, -1.5]}>
      <mesh>
        <sphereGeometry args={[1.28, 64, 64]} />
        <meshStandardMaterial color="#08111f" roughness={0.55} metalness={0.2} emissive="#0c4a6e" emissiveIntensity={0.25} wireframe />
      </mesh>
      {markers.map((marker) => (
        <mesh key={marker.ticker} position={marker.pos as [number, number, number]} onClick={(event) => { event.stopPropagation(); onSelectTicker(marker.ticker); }} scale={selectedTicker === marker.ticker ? 1.45 : 1}>
          <sphereGeometry args={[0.055, 18, 18]} />
          <meshStandardMaterial color={marker.color} emissive={marker.color} emissiveIntensity={1.7} />
        </mesh>
      ))}
    </group>
  );
}
