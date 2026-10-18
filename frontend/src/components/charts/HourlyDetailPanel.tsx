import { DatasetResults } from '../../types';
import { Card } from '../common/Card';
import { SOURCE_COLORS, SOURCE_NAMES, SourceId } from '../../utils/colors';
import { formatNumber, formatPercent } from '../../utils/formatters';

interface HourlyDetailPanelProps {
  results: DatasetResults;
  hourIndex: number | null;
  onClearPin: () => void;
}

export function HourlyDetailPanel({
  results,
  hourIndex,
  onClearPin,
}: HourlyDetailPanelProps) {
  const times = results.times || [];
  const obs = results.observed_pm25_popw || [];
  const hourly = results.hourly || {};

  // If no hour is pinned, pick the worst hour
  const defaultWorstIndex = obs.indexOf(Math.max(...obs));
  const activeIndex = hourIndex !== null ? hourIndex : defaultWorstIndex;
  const isPinned = hourIndex !== null;

  if (activeIndex < 0 || activeIndex >= times.length) return null;

  const timeLabel = times[activeIndex];
  const observedVal = obs[activeIndex];

  const sourceOrder: SourceId[] = ['traffic', 'industry', 'dust', 'biomass', 'background'];

  const contributions = sourceOrder.map(src => {
    const val = hourly[src]?.mean?.[activeIndex] || 0;
    return {
      src,
      name: SOURCE_NAMES[src],
      color: SOURCE_COLORS[src],
      val,
    };
  });

  const totalModelled = contributions.reduce((acc, c) => acc + c.val, 0);

  return (
    <Card className="p-5 space-y-4">
      <div className="flex items-center justify-between border-b border-slate-100 pb-3">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="font-bold text-slate-900 text-sm">
              {isPinned ? 'Pinned Hour Breakdown' : 'Peak Smog Hour (Worst)'}
            </h3>
            {isPinned && (
              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-50 text-blue-700">
                Pinned
              </span>
            )}
          </div>
          <div className="text-xs text-slate-500 mt-0.5">{timeLabel}</div>
        </div>

        {isPinned && (
          <button
            onClick={onClearPin}
            className="text-xs font-semibold text-slate-400 hover:text-slate-700"
          >
            Clear Pin
          </button>
        )}
      </div>

      {/* Hourly Stacked Mini-Bar */}
      <div className="space-y-1.5">
        <div className="flex justify-between text-xs font-semibold">
          <span className="text-slate-600">Total Smog at this hour</span>
          <span className="text-slate-900">
            {formatNumber(totalModelled, 0)} µg/m³
            {observedVal !== undefined && (
              <span className="text-slate-400 font-normal">
                {' '}
                (observed: {formatNumber(observedVal, 0)})
              </span>
            )}
          </span>
        </div>
        <div className="flex h-3 w-full rounded-full overflow-hidden bg-slate-100">
          {contributions.map(c => {
            const pct = totalModelled > 0 ? (c.val / totalModelled) * 100 : 0;
            return (
              <div
                key={c.src}
                style={{ width: `${pct}%`, backgroundColor: c.color }}
                title={`${c.name}: ${formatNumber(c.val, 0)} µg/m³`}
                className="h-full"
              />
            );
          })}
        </div>
      </div>

      {/* Breakdown List */}
      <div className="space-y-2 pt-2">
        {contributions.map(c => {
          const share = totalModelled > 0 ? c.val / totalModelled : 0;
          return (
            <div key={c.src} className="flex items-center justify-between text-xs">
              <div className="flex items-center gap-2">
                <span
                  className="w-2.5 h-2.5 rounded-full"
                  style={{ backgroundColor: c.color }}
                />
                <span className="font-medium text-slate-700">{c.name}</span>
              </div>
              <div className="flex items-center gap-3">
                <span className="font-semibold text-slate-900">
                  {formatNumber(c.val, 1)} µg/m³
                </span>
                <span className="text-slate-400 w-10 text-right">
                  {formatPercent(share)}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
}
