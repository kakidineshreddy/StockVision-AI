export function LoadingSpinner() {
  return (
    <div className="flex flex-col items-center gap-3 text-zinc-300">
      <div className="h-12 w-12 animate-spin rounded-full border-2 border-cyan-300/20 border-t-cyan-300" />
      <span className="text-sm">Loading market intelligence</span>
    </div>
  );
}
