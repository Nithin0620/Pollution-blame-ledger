import { MapPin, UploadCloud, BookOpen, Layers } from 'lucide-react';
import { DatasetSummary } from '../../types';

interface NavbarProps {
  datasets: DatasetSummary[];
  selectedId: string;
  onSelectDataset: (id: string) => void;
  activeView: string;
  onNavigate: (view: string) => void;
}

export function Navbar({
  datasets,
  selectedId,
  onSelectDataset,
  activeView,
  onNavigate,
}: NavbarProps) {
  return (
    <header className="sticky top-0 z-40 bg-white/90 backdrop-blur-md border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => onNavigate('dashboard')}
            className="flex items-center gap-2.5 font-extrabold text-slate-900 tracking-tight text-lg hover:opacity-90"
          >
            <div className="w-8 h-8 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
              <MapPin className="w-4 h-4" />
            </div>
            <span>Pollution Blame Ledger</span>
          </button>
          <span className="hidden sm:inline-block px-2 py-0.5 rounded text-[11px] font-bold tracking-wider uppercase bg-blue-50 text-blue-700 border border-blue-200/60">
            Delhi NCR
          </span>
        </div>

        {/* Dataset Selector */}
        <div className="flex-1 max-w-sm hidden md:block">
          <div className="relative">
            <select
              value={selectedId}
              onChange={e => onSelectDataset(e.target.value)}
              className="w-full bg-slate-50 border border-slate-300 text-slate-800 text-xs font-semibold rounded-xl px-3 py-2 pr-8 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 truncate"
            >
              {datasets.map(d => (
                <option key={d.id} value={d.id}>
                  {d.kind === 'synthetic' ? '🧪 ' : '📍 '}
                  {d.name} ({Math.round(d.total_pm25_mean)} µg/m³)
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Nav Links */}
        <nav className="flex items-center gap-1.5 sm:gap-2">
          <button
            onClick={() => onNavigate('dashboard')}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-colors inline-flex items-center gap-1.5 ${
              activeView === 'dashboard'
                ? 'bg-blue-50 text-blue-700'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>Dashboard</span>
          </button>

          <button
            onClick={() => onNavigate('learn')}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-colors inline-flex items-center gap-1.5 ${
              activeView === 'learn'
                ? 'bg-blue-50 text-blue-700'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            <BookOpen className="w-3.5 h-3.5" />
            <span>How it Works</span>
          </button>

          <button
            onClick={() => onNavigate('upload')}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-colors inline-flex items-center gap-1.5 ${
              activeView === 'upload'
                ? 'bg-blue-600 text-white shadow-sm shadow-blue-500/20'
                : 'bg-slate-900 text-white hover:bg-slate-800'
            }`}
          >
            <UploadCloud className="w-3.5 h-3.5" />
            <span>Upload CSV</span>
          </button>
        </nav>
      </div>
    </header>
  );
}
