import { SOURCE_COLORS, SourceId } from '../../utils/colors';

interface ScatterPoint {
  truth: number;
  est: number;
  lo: number;
  hi: number;
  source: string;
}

interface CredibleIntervalWhiskerProps {
  points: ScatterPoint[];
}

export function CredibleIntervalWhisker({ points }: CredibleIntervalWhiskerProps) {
  if (!points || points.length === 0) {
    return <div className="text-xs text-slate-400">No calibration points available.</div>;
  }

  const width = 420;
  const height = 300;
  const m = { l: 45, r: 15, t: 15, b: 35 };

  const maxVal = Math.max(...points.map(p => Math.max(p.truth, p.hi))) * 1.05;

  const getX = (val: number) => m.l + (val / maxVal) * (width - m.l - m.r);
  const getY = (val: number) => height - m.b - (val / maxVal) * (height - m.b - m.t);

  const gridSteps = [0, maxVal * 0.25, maxVal * 0.5, maxVal * 0.75, maxVal];

  return (
    <div className="space-y-2">
      <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">
        Truth vs. Model Recovery (Held-Out Synthetic Episodes)
      </div>

      <div className="border border-slate-200/90 rounded-2xl bg-white p-2">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="w-full h-auto"
          role="img"
          aria-label="True vs posterior scatter plot"
        >
          {/* 1:1 Identity Line */}
          <line
            x1={getX(0)}
            y1={getY(0)}
            x2={getX(maxVal)}
            y2={getY(maxVal)}
            stroke="#94a3b8"
            strokeDasharray="4 4"
            strokeWidth={1.5}
          />

          {/* Grid lines & axis labels */}
          {gridSteps.map((v, i) => (
            <g key={i}>
              <line
                x1={m.l}
                y1={getY(v)}
                x2={width - m.r}
                y2={getY(v)}
                stroke="#f1f5f9"
                strokeWidth={1}
              />
              <text
                x={m.l - 8}
                y={getY(v) + 4}
                textAnchor="end"
                className="text-[9px] fill-slate-400"
              >
                {Math.round(v)}
              </text>
              <text
                x={getX(v)}
                y={height - m.b + 14}
                textAnchor="middle"
                className="text-[9px] fill-slate-400"
              >
                {Math.round(v)}
              </text>
            </g>
          ))}

          {/* Points & Whiskers */}
          {points.map((p, i) => {
            const color = SOURCE_COLORS[p.source as SourceId] || '#2563eb';
            const cx = getX(p.truth);
            const cy = getY(p.est);
            const yLo = getY(p.lo);
            const yHi = getY(p.hi);

            return (
              <g key={i}>
                {/* 90% CI whisker bar */}
                <line
                  x1={cx}
                  y1={yLo}
                  x2={cx}
                  y2={yHi}
                  stroke={color}
                  strokeWidth={1.5}
                  opacity={0.5}
                />
                {/* Posterior Mean dot */}
                <circle
                  cx={cx}
                  cy={cy}
                  r={3.2}
                  fill={color}
                  stroke="#ffffff"
                  strokeWidth={1}
                />
              </g>
            );
          })}

          {/* Axis Titles */}
          <text
            x={(width + m.l) / 2}
            y={height - 4}
            textAnchor="middle"
            className="text-[10px] font-semibold fill-slate-600"
          >
            True Known Contribution (µg/m³)
          </text>
          <text
            transform={`translate(12, ${height / 2}) rotate(-90)`}
            textAnchor="middle"
            className="text-[10px] font-semibold fill-slate-600"
          >
            Posterior Mean & 90% CI
          </text>
        </svg>
      </div>
    </div>
  );
}
