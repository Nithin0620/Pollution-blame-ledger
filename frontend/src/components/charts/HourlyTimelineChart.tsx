import { useState, useMemo } from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine,
} from 'recharts';
import { DatasetResults } from '../../types';
import { SOURCE_COLORS, SOURCE_SHORT_NAMES, SourceId } from '../../utils/colors';
import { formatNumber, WHO_24H_GUIDELINE } from '../../utils/formatters';

interface HourlyTimelineChartProps {
  results: DatasetResults;
  pinnedHour: number | null;
  onPinHour: (hourIndex: number | null) => void;
}

export function HourlyTimelineChart({
  results,
  pinnedHour,
  onPinHour,
}: HourlyTimelineChartProps) {
  const [hiddenSources, setHiddenSources] = useState<Set<SourceId>>(new Set());

  const sourceOrder: SourceId[] = ['background', 'biomass', 'traffic', 'dust', 'industry'];

  // Toggle source in/out of chart
  const toggleSource = (source: SourceId) => {
    setHiddenSources(prev => {
      const next = new Set(prev);
      if (next.has(source)) {
        next.delete(source);
      } else {
        next.add(source);
      }
      return next;
    });
  };

  // Build chart dataset
  const chartData = useMemo(() => {
    const times = results.times || [];
    const obs = results.observed_pm25_popw || [];
    const hourly = results.hourly || {};

    return times.map((t, i) => {
      const point: any = {
        index: i,
        time: t.length > 16 ? t.slice(5, 16).replace('T', ' ') : t,
        observed: obs[i] !== undefined ? Math.round(obs[i]) : null,
      };

      for (const src of sourceOrder) {
        if (!hiddenSources.has(src) && hourly[src]?.mean) {
          point[src] = Math.round(hourly[src].mean[i] || 0);
        } else {
          point[src] = 0;
        }
      }

      return point;
    });
  }, [results, hiddenSources]);

  return (
    <div className="space-y-4">
      {/* Interactive Legend Toggles */}
      <div className="flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex flex-wrap items-center gap-2">
          <span className="font-bold text-slate-500 uppercase tracking-wider text-[11px] mr-1">
            Toggle Sources:
          </span>
          {sourceOrder.map(src => {
            const isHidden = hiddenSources.has(src);
            return (
              <button
                key={src}
                onClick={() => toggleSource(src)}
                className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg border text-xs font-semibold transition-all ${
                  isHidden
                    ? 'bg-slate-100 text-slate-400 border-slate-200 line-through'
                    : 'bg-white text-slate-800 border-slate-300 shadow-sm'
                }`}
              >
                <span
                  className="w-2.5 h-2.5 rounded-full"
                  style={{ backgroundColor: isHidden ? '#cbd5e1' : SOURCE_COLORS[src] }}
                />
                <span>{SOURCE_SHORT_NAMES[src]}</span>
              </button>
            );
          })}
        </div>

        <div className="text-xs text-slate-400 font-medium">
          Click any point to pin hour
        </div>
      </div>

      {/* Chart */}
      <div className="h-80 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={chartData}
            onClick={e => {
              if (e && e.activeTooltipIndex !== undefined) {
                onPinHour(e.activeTooltipIndex);
              }
            }}
            margin={{ top: 10, right: 10, left: -10, bottom: 0 }}
          >
            <defs>
              {sourceOrder.map(src => (
                <linearGradient key={src} id={`grad-${src}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={SOURCE_COLORS[src]} stopOpacity={0.8} />
                  <stop offset="95%" stopColor={SOURCE_COLORS[src]} stopOpacity={0.6} />
                </linearGradient>
              ))}
            </defs>

            <XAxis
              dataKey="time"
              tickLine={false}
              axisLine={false}
              tick={{ fill: '#94a3b8', fontSize: 11 }}
              interval={Math.floor(chartData.length / 8)}
            />
            <YAxis
              tickLine={false}
              axisLine={false}
              tick={{ fill: '#94a3b8', fontSize: 11 }}
            />

            <Tooltip
              content={({ active, payload, label }) => {
                if (!active || !payload || !payload.length) return null;
                const point = payload[0]?.payload;
                const total = sourceOrder.reduce((acc, src) => acc + (point[src] || 0), 0);

                return (
                  <div className="bg-slate-900/95 text-white p-3 rounded-xl shadow-xl text-xs space-y-1.5 border border-slate-800 min-w-[180px]">
                    <div className="font-bold text-slate-300 border-b border-slate-800 pb-1 flex justify-between">
                      <span>{label}</span>
                      <span>Total: {formatNumber(total, 0)} µg/m³</span>
                    </div>
                    {sourceOrder.map(src => {
                      if (hiddenSources.has(src)) return null;
                      const val = point[src] || 0;
                      return (
                        <div key={src} className="flex items-center justify-between gap-4">
                          <span className="flex items-center gap-1.5 text-slate-300">
                            <span
                              className="w-2 h-2 rounded-full"
                              style={{ backgroundColor: SOURCE_COLORS[src] }}
                            />
                            {SOURCE_SHORT_NAMES[src]}
                          </span>
                          <span className="font-semibold">{formatNumber(val, 0)} µg/m³</span>
                        </div>
                      );
                    })}
                    {point.observed !== null && (
                      <div className="pt-1 border-t border-slate-800 flex justify-between text-blue-300 font-bold">
                        <span>Observed PM₂.₅:</span>
                        <span>{formatNumber(point.observed, 0)} µg/m³</span>
                      </div>
                    )}
                  </div>
                );
              }}
            />

            <ReferenceLine
              y={WHO_24H_GUIDELINE}
              stroke="#16a34a"
              strokeDasharray="4 4"
              label={{
                value: 'WHO 15 µg/m³',
                fill: '#16a34a',
                fontSize: 10,
                position: 'insideTopLeft',
              }}
            />

            {pinnedHour !== null && (
              <ReferenceLine
                x={chartData[pinnedHour]?.time}
                stroke="#0f172a"
                strokeWidth={2}
              />
            )}

            {sourceOrder.map(src => (
              <Area
                key={src}
                type="monotone"
                dataKey={src}
                stackId="1"
                stroke={SOURCE_COLORS[src]}
                fill={`url(#grad-${src})`}
              />
            ))}
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
