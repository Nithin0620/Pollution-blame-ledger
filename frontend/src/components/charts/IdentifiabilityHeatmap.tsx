import { SOURCE_SHORT_NAMES, SourceId } from '../../utils/colors';

interface IdentifiabilityHeatmapProps {
  names: string[];
  matrix?: number[][];
}

export function IdentifiabilityHeatmap({ names, matrix }: IdentifiabilityHeatmapProps) {
  if (!matrix || matrix.length === 0 || !names || names.length === 0) {
    return (
      <div className="text-xs text-slate-400 p-4">
        Correlation matrix not available for this run.
      </div>
    );
  }

  const n = names.length;
  const cellSize = 38;
  const labelWidth = 65;
  const width = labelWidth + n * cellSize;
  const height = labelWidth + n * cellSize;

  const getColor = (val: number) => {
    if (val === 1) return '#f1f5f9';
    if (val < 0) {
      // Negative correlation: rose/red
      const intensity = Math.min(1, Math.abs(val));
      return `rgba(239, 68, 68, ${0.15 + intensity * 0.75})`;
    }
    // Positive correlation: blue
    const intensity = Math.min(1, val);
    return `rgba(37, 99, 235, ${0.15 + intensity * 0.75})`;
  };

  return (
    <div className="space-y-2">
      <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">
        Posterior Correlation Matrix (Identifiability Diagnostic)
      </div>

      <div className="border border-slate-200/90 rounded-2xl bg-white p-3 overflow-x-auto">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          style={{ width: `${width}px`, height: `${height}px` }}
          className="mx-auto"
        >
          {/* Column Headers */}
          {names.map((name, j) => (
            <text
              key={`col-${j}`}
              x={labelWidth + j * cellSize + cellSize / 2}
              y={labelWidth - 10}
              textAnchor="start"
              transform={`rotate(-45, ${labelWidth + j * cellSize + cellSize / 2}, ${labelWidth - 10})`}
              className="text-[10px] font-semibold fill-slate-600"
            >
              {SOURCE_SHORT_NAMES[name as SourceId] || name}
            </text>
          ))}

          {/* Rows */}
          {matrix.map((row, i) => (
            <g key={`row-${i}`}>
              {/* Row Header */}
              <text
                x={labelWidth - 8}
                y={labelWidth + i * cellSize + cellSize / 2 + 3}
                textAnchor="end"
                className="text-[10px] font-semibold fill-slate-600"
              >
                {SOURCE_SHORT_NAMES[names[i] as SourceId] || names[i]}
              </text>

              {/* Cells */}
              {row.map((val, j) => {
                const x = labelWidth + j * cellSize;
                const y = labelWidth + i * cellSize;
                return (
                  <g key={`cell-${i}-${j}`}>
                    <rect
                      x={x + 1}
                      y={y + 1}
                      width={cellSize - 2}
                      height={cellSize - 2}
                      rx={6}
                      fill={getColor(val)}
                    />
                    <text
                      x={x + cellSize / 2}
                      y={y + cellSize / 2 + 3}
                      textAnchor="middle"
                      className={`text-[9px] font-bold ${
                        Math.abs(val) > 0.4 ? 'fill-slate-900' : 'fill-slate-500'
                      }`}
                    >
                      {val.toFixed(2)}
                    </text>
                  </g>
                );
              })}
            </g>
          ))}
        </svg>

        <p className="text-[11px] text-slate-500 mt-2 text-center">
          <span className="text-rose-600 font-bold">Red cells</span> = Strong negative collinearity (sources compensate for each other and can only be robustly reported as a joint sum).
        </p>
      </div>
    </div>
  );
}
