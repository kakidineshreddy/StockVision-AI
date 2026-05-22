import { useState } from 'react';
import { BrainCircuit } from 'lucide-react';
import { apiService } from '../../services/api';

export function TrainButton({ ticker }: { ticker: string }) {
  const [busy, setBusy] = useState(false);
  return (
    <button
      className="inline-flex h-10 items-center gap-2 rounded-md border border-fuchsia-300/20 bg-fuchsia-400/10 px-3 text-sm font-semibold text-fuchsia-100 transition hover:border-fuchsia-200/60 hover:bg-fuchsia-400/20 disabled:opacity-60"
      disabled={busy}
      onClick={async () => { setBusy(true); try { await apiService.trainModel(ticker); } finally { setTimeout(() => setBusy(false), 700); } }}
    >
      <BrainCircuit size={17} />
      {busy ? 'Training' : 'Train'}
    </button>
  );
}
