import { Text } from '@react-three/drei';
import { useFrame } from '@react-three/fiber';
import { useRef } from 'react';
import * as THREE from 'three';

export function FloatingTicker({ ticker, signal }: { ticker: string; signal: string }) {
  const group = useRef<THREE.Group>(null);
  useFrame(({ clock }) => { if (group.current) group.current.position.y = 1.35 + Math.sin(clock.elapsedTime * 1.4) * 0.08; });
  const color = signal === 'BUY' ? '#22c55e' : signal === 'SELL' ? '#ef4444' : '#f59e0b';
  return (
    <group ref={group} position={[0, 1.35, -1.7]}>
      <Text fontSize={0.5} anchorX="center" anchorY="middle" color="#f8fafc" outlineColor="#000" outlineWidth={0.02}>{ticker}</Text>
      <Text position={[0, -0.48, 0]} fontSize={0.18} anchorX="center" anchorY="middle" color={color}>{signal}</Text>
    </group>
  );
}
