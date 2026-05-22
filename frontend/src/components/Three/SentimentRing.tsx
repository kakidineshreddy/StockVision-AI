import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { sentimentColor } from '../../utils/animations';

export function SentimentRing({ score }: { score: number }) {
  const ref = useRef<THREE.Mesh>(null);
  useFrame((_, delta) => { if (ref.current) ref.current.rotation.z += delta * 0.25; });
  return (
    <mesh ref={ref} position={[0, 1.85, -2.5]} rotation={[Math.PI / 2.4, 0, 0]}>
      <torusGeometry args={[0.9, 0.035 + Math.abs(score) * 0.025, 16, 96]} />
      <meshStandardMaterial color={sentimentColor(score)} emissive={sentimentColor(score)} emissiveIntensity={1.2} />
    </mesh>
  );
}
