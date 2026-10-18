import { useState } from 'react';
import { SOURCE_SHORT_NAMES, SourceId } from '../../utils/colors';
import { formatPercent } from '../../utils/formatters';

interface BaselinesTableProps {
  baselines: any;
  shiftTest: any;
}

export function BaselinesTable({ baselines, shiftTest }: BaselinesTableProps) {
  const [view, setView] = useState<'shift' | 'familiar'>('shift');

  if (!baselines) {
    return (
      <div className="text-xs text-slate-400 p-4">
        Baseline comparative validation not run for this build.
      </div>
    );
  }

  const activeData = view === 'shift' && shiftTest ? shiftTest : baselines;
  const sources: SourceId[] = ['traffic', 'biomass', 'dust', 'industry', 'background'];

  return (
    <div className="space-y-3">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">
          Performance Benchmarking Against Simpler Models
        </div>
        <div className="inline-flex rounded-xl bg-slate-100 p-1 text-xs">
          <button
            onClick={() => setView('shift')}
            className={`px-3 py-1 rounded-lg font-bold transition-all ${
              view === 'shift'
                ? 'bg-white text-blue-700 shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Shifted Stress Test
          </button>
          <button
            onClick={() => setView('familiar')}
            className={`px-3 py-1 rounded-lg font-bold transition-all ${
              view === 'familiar'
                ? 'bg-white text-blue-700 shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Familiar Episodes
          </button>
        </div>
      </div>

      <div className="border border-slate-200/90 rounded-2xl overflow-hidden bg-white">
        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-600 font-bold uppercase tracking-wider text-[10px]">
              <tr>
                <th className="px-4 py-3">Source Category</th>
                <th className="px-4 py-3 text-right">Bayesian Ledger</th>
                <th className="px-4 py-3 text-right">Least Squares (NNLS)</th>
                <th className="px-4 py-3 text-right">Fixed Published Split</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {sources.map(src => {
                const bayesErr = activeData.bayes?.[src]?.rel_err_median;
                const nnlsErr = activeData.nnls?.[src]?.rel_err_median;
                const fixedErr = activeData.fixed_shares?.[src]?.rel_err_median;

                const minErr = Math.min(
                  bayesErr ?? 999,
                  nnlsErr ?? 999,
                  fixedErr ?? 999
                );

                return (
                  <tr key={src} className="hover:bg-slate-50/50">
                    <td className="px-4 py-2.5 font-bold text-slate-800">
                      {SOURCE_SHORT_NAMES[src]}
                    </td>
                    <td
                      className={`px-4 py-2.5 text-right font-semibold ${
                        bayesErr === minErr ? 'text-emerald-700 bg-emerald-50/50' : 'text-slate-700'
                      }`}
                    >
                      {bayesErr != null ? formatPercent(bayesErr) : '-'}
                    </td>
                    <td
                      className={`px-4 py-2.5 text-right font-semibold ${
                        nnlsErr === minErr ? 'text-emerald-700 bg-emerald-50/50' : 'text-slate-700'
                      }`}
                    >
                      {nnlsErr != null ? formatPercent(nnlsErr) : '-'}
                    </td>
                    <td
                      className={`px-4 py-2.5 text-right font-semibold ${
                        fixedErr === minErr ? 'text-emerald-700 bg-emerald-50/50' : 'text-slate-700'
                      }`}
                    >
                      {fixedErr != null ? formatPercent(fixedErr) : '-'}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      <p className="text-[11px] text-slate-500 leading-relaxed">
        <span className="font-bold text-slate-700">Key takeaway:</span> A fixed historical split works reasonably well when air matches historical winter averages, but fails when unusual events occur. The Bayesian ledger provides calibrated uncertainty intervals that encompass the truth even under novel meteorological shifts.
      </p>
    </div>
  );
}
