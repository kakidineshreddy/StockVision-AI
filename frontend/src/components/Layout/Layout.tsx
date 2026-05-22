import { Header } from './Header';
import { Sidebar } from './Sidebar';

export function Layout({ children, ticker }: { children: React.ReactNode; ticker: string }) {
  return (
    <div className="min-h-screen bg-black text-zinc-100">
      <Header ticker={ticker} />
      <Sidebar />
      {children}
    </div>
  );
}
