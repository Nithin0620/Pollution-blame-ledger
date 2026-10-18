import { LiteratureComparisonItem } from '../../types';
import { SOURCE_COLORS, SOURCE_SHORT_NAMES, SourceId } from '../../utils/colors';
import { formatPercent } from '../../utils/formatters';

interface LiteratureComparisonProps {
  literature?: Record<string, LiteratureComparisonItem>;
}

export function LiteratureComparison({ literature }: LiteratureComparisonProps) {
  if (!literature || Object.keys(literature).length === 0) {
    return (
      <div className="text-xs text-slate-400 p-4">
        Literature validation comparisons not available for this run.
      </div>
    );
  }

  const sources: SourceId[] = ['traffic', 'biomass', 'dust', 'industry'];
  const width = 360;
  const height = 36;
  const lo = 0;
  const hi = 60;
  const getX = (val: number) => 10 + ((val - lo) / (hi - lo)) * (width - 20);

  return (
    <div className="space-y-4">
      <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">
        Comparison With Published Delhi Studies
      </div>

      <div className="border border-slate-200/90 rounded-2xl bg-white p-4 divide-y divide-slate-100">
        {sources.map(src => {
          const item = literature[src];
          if (!item) return null;

          const color = SOURCE_COLORS[src];
          const name = SOURCE_SHORT_NAMES[src];
          const hasOverlap = item.refs.some(r => r.overlaps);

          return (
            <div key={src} className="py-3 first:pt-0 last:pb-0 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div className="min-w-[130px]">
                <div className="font-bold text-xs text-slate-900">{name}</div>
                <div className="text-[11px] text-slate-500">
                  Ledger: {formatPercent(item.ours.mean / 100)} ({formatPercent(item.ours.lo / 100)}–{formatPercent(item.ours.hi / 100)})
                </div>
                <span
                  className={`inline-block mt-1 text-[10px] font-bold px-2 py-0.5 rounded-full ${
                    hasOverlap
                      ? 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                      : 'bg-amber-50 text-amber-800 border border-amber-200'
                  }`}
                >
                  {hasOverlap ? 'Overlaps study' : 'Outside studies'}
                </span>
              </div>

              {/* Graphic Whisker Bar */}
              <div className="flex-1 max-w-xs">
                <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-8">
                  <line
                    x1={10}
                    y1={height - 8}
                    x2={width - 10}
                    y2={height - 8}
                    stroke="#e2e8f0"
                  />
                  {[0, 20, 40, 60].map(v => (
                    <text
                      key={v}
                      x={getX(v)}
                      y={height}
                      textAnchor="middle"
                      className="text-[8px] fill-slate-400"
                    >
                      {v}%
                    </text>
                  ))}

                  {/* Published ranges (Dark bands) */}
                  {item.refs.map((r, ri) => {
                    const xLo = getX(r.low);
                    const xHi = getX(r.high);
                    return (
                      <rect
                        key={ri}
                        x={xLo}
                        y={4}
                        width={Math.max(3, xHi - xLo)}
                        height={18}
                        rx={3}
                        fill="#0f172a"
                        opacity={0.16}
                      />
                    );
                  })}

                  {/* Our Credible Interval Bar */}
                  <rect
                    x={getX(item.ours.lo)}
                    y={10}
                    width={Math.max(4, getX(item.ours.hi) - getX(item.ours.lo))}
                    height={6}
                    rx={3}
                    fill={color}
                  />
                  <circle
                    cx={getX(item.ours.mean)}
                    cy={13}
                    r={3.5}
                    fill="#ffffff"
                    stroke={color}
                    strokeWidth={2}
                  />
                </svg>
              </div>
            </div>
          );
        })}
      </div>

      <p className="text-[11px] text-slate-500 leading-relaxed">
        Dark shaded bands represent published literature estimates (CEEW 2019 emissions inventory & CSE / IIT Kanpur winter source apportionment). Colored bars represent our 90% credible intervals.
      </p>
    </div>
  );
}
