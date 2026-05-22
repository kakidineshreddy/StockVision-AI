import { Canvas } from '@react-three/fiber';
import { OrbitControls, Stars } from '@react-three/drei';
import { PredictionData, StockHistoryItem } from '../../types';
import { ParticleField } from './ParticleField';
import { StockGlobe } from './StockGlobe';
import { PriceTower } from './PriceTower';
import { SentimentRing } from './SentimentRing';
import { FloatingTicker } from './FloatingTicker';

export function Scene3D({ selectedTicker, onSelectTicker, prediction, history }: { selectedTicker: string; onSelectTicker: (ticker: string) => void; prediction: PredictionData | null; history: StockHistoryItem[] }) {
  return (
    <div className="fixed inset-0 z-0 opacity-80">
      <Canvas camera={{ position: [0, 3.2, 8.5], fov: 48 }} dpr={[1, 1.75]} gl={{ antialias: true }}>
        <color attach="background" args={['#050505']} />
        <fog attach="fog" args={['#050505', 8, 22]} />
        <ambientLight intensity={0.55} />
        <directionalLight position={[4, 8, 4]} intensity={1.5} color="#e0f2fe" />
        <pointLight position={[-4, 2, 3]} intensity={3} color="#d946ef" />
        <Stars radius={50} depth={20} count={1200} factor={2} fade speed={0.5} />
        <ParticleField />
        <group position={[0, 0.2, 0]}>
          <StockGlobe selectedTicker={selectedTicker} onSelectTicker={onSelectTicker} />
          <PriceTower history={history} prediction={prediction} />
          <SentimentRing score={prediction?.sentiment_score ?? 0} />
          <FloatingTicker ticker={selectedTicker} signal={prediction?.signal ?? 'HOLD'} />
        </group>
        <OrbitControls enablePan={false} enableZoom={false} autoRotate autoRotateSpeed={0.25} maxPolarAngle={Math.PI / 1.9} minPolarAngle={Math.PI / 3.2} />
      </Canvas>
    </div>
  );
}
