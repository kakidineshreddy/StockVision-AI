import { BarChart3, Globe2, LineChart, RadioTower } from 'lucide-react';

const items = [
  { icon: BarChart3, label: 'Dashboard' },
  { icon: LineChart, label: 'Charts' },
  { icon: Globe2, label: 'Markets' },
  { icon: RadioTower, label: 'Live' },
];

export function Sidebar() {
  return (
    <nav className="fixed left-3 top-20 z-20 hidden w-14 flex-col gap-2 rounded-lg border border-white/10 bg-black/45 p-2 backdrop-blur-xl 2xl:flex">
      {items.map(({ icon: Icon, label }, index) => (
        <button key={label} className={`icon-button ${index === 0 ? 'border-cyan-300/40 bg-cyan-300/10 text-cyan-100' : ''}`} title={label}>
          <Icon size={18} />
        </button>
      ))}
    </nav>
  );
}
