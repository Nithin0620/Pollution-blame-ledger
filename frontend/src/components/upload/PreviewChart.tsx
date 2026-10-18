import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, ReferenceLine } from 'recharts';
import { PreviewPoint } from '../../types';
import { WHO_24H_GUIDELINE, formatNumber } from '../../utils/formatters';

interface PreviewChartProps {
  points: PreviewPoint[];
}

export function PreviewChart({ points }: PreviewChartProps) {
  if (!points || points.length === 0) return null;

  return (
    <div className="space-y-2">
      <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">
        PM₂.₅ Time Series Preview (Sampled Hours)
      </div>

      <div className="h-44 w-full border border-slate-200/90 rounded-2xl bg-white p-2">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={points} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
            <XAxis
              dataKey="hour"
              tickLine={false}
              axisLine={false}
              tick={{ fill: '#94a3b8', fontSize: 10 }}
              label={{ value: 'Time (Hours) →', position: 'insideBottomRight', offset: -4, fill: '#94a3b8', fontSize: 9 }}
            />
            <YAxis
              tickLine={false}
              axisLine={false}
              tick={{ fill: '#94a3b8', fontSize: 10 }}
            />
            <Tooltip
              content={({ active, payload }) => {
                if (!active || !payload || !payload.length) return null;
                const val = payload[0].value as number;
                return (
                  <div className="bg-slate-900 text-white px-2.5 py-1.5 rounded-lg text-xs font-semibold">
                    PM₂.₅: {formatNumber(val, 1)} µg/m³
                  </div>
                );
              }}
            />
            <ReferenceLine
              y={WHO_24H_GUIDELINE}
              stroke="#16a34a"
              strokeDasharray="3 3"
              label={{ value: 'WHO 15', fill: '#16a34a', fontSize: 9, position: 'insideTopLeft' }}
            />
            <Line
              type="monotone"
              dataKey="pm25"
              stroke="#2563eb"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
