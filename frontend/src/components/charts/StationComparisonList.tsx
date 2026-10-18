import { StationData } from '../../types';
import { SOURCE_COLORS, SourceId } from '../../utils/colors';
import { formatNumber } from '../../utils/formatters';

interface StationComparisonListProps {
  stations: StationData[];
  selectedStation: string | null;
  onSelectStation: (stationName: string | null) => void;
}

export function StationComparisonList({
  stations,
  selectedStation,
  onSelectStation,
}: StationComparisonListProps) {
  const order: SourceId[] = ['traffic', 'industry', 'dust', 'biomass', 'background'];

  return (
    <div className="space-y-2">
      <div className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
        Monitoring Station Comparisons
      </div>

      <div className="space-y-1.5 max-h-[360px] overflow-y-auto pr-1">
        {stations.map(s => {
          const tot =
            order.reduce((acc, k) => acc + (k === 'background' ? s.background : s.ugm3[k] || 0), 0) || 1;
          const isSelected = selectedStation === s.station;

          return (
            <div
              key={s.station}
              onClick={() => onSelectStation(isSelected ? null : s.station)}
              className={`p-3 rounded-xl border text-xs cursor-pointer transition-all flex items-center justify-between gap-3 ${
                isSelected
                  ? 'bg-blue-50/70 border-blue-300 shadow-sm'
                  : 'bg-white border-slate-200 hover:border-slate-300'
              }`}
            >
              <div className="min-w-[120px] font-bold text-slate-800 truncate">
                {s.station}
              </div>

              {/* Proportional Mini Bar */}
              <div className="flex-1 flex h-3 rounded-full overflow-hidden bg-slate-100">
                {order.map(k => {
                  const val = k === 'background' ? s.background : s.ugm3[k] || 0;
                  const pct = (val / tot) * 100;
                  return (
                    <div
                      key={k}
                      style={{ width: `${pct}%`, backgroundColor: SOURCE_COLORS[k] }}
                      title={`${k}: ${formatNumber(val, 0)} µg/m³`}
                      className="h-full"
                    />
                  );
                })}
              </div>

              <div className="text-right min-w-[50px] font-black text-slate-900">
                {formatNumber(s.observed_pm25, 0)}{' '}
                <span className="text-[10px] text-slate-400 font-normal">µg/m³</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
