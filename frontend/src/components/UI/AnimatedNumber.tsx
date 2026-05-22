import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

export function AnimatedNumber({ value, formatter = (n) => n.toFixed(2), className = '' }: { value: number; formatter?: (value: number) => string; className?: string }) {
  const [shown, setShown] = useState(value);
  useEffect(() => {
    const start = shown;
    const delta = value - start;
    let frame = 0;
    const total = 24;
    const id = window.setInterval(() => {
      frame += 1;
      setShown(start + delta * (1 - Math.pow(1 - frame / total, 3)));
      if (frame >= total) window.clearInterval(id);
    }, 16);
    return () => window.clearInterval(id);
  }, [value]);
  return <motion.span animate={{ opacity: [0.7, 1] }} className={className}>{formatter(shown)}</motion.span>;
}
