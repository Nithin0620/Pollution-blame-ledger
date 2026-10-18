import { useState } from 'react';
import { StationData } from '../../types';
import { SOURCE_COLORS, SOURCE_NAMES, SourceId } from '../../utils/colors';
import { formatNumber } from '../../utils/formatters';

interface StationScatterMapProps {
  stations: StationData[];
  selectedStation: string | null;
  onSelectStation: (stationName: string | null) => void;
}

export function StationScatterMap({
  stations,
  selectedStation,
  onSelectStation,
}: StationScatterMapProps) {
  const [hoveredStation, setHoveredStation] = useState<StationData | null>(null);

  const validStations = stations.filter(s => s.lat != null && s.lon != null);

  if (validStations.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-slate-400 text-xs">
        No geographic coordinates available for this dataset.
      </div>
    );
  }

  const lats = validStations.map(s => s.lat as number);
  const lons = validStations.map(s => s.lon as number);
  const minLat = Math.min(...lats);
  const maxLat = Math.max(...lats);
  const minLon = Math.min(...lons);
  const maxLon = Math.max(...lons);

  const maxObs = Math.max(...validStations.map(s => s.observed_pm25));

  const width = 450;
  const height = 320;
  const padding = 45;

  const getX = (lon: number) => {
    const span = maxLon - minLon || 0.01;
    return padding + ((lon - minLon) / span) * (width - 2 * padding);
  };

  const getY = (lat: number) => {
    const span = maxLat - minLat || 0.01;
    return height - padding - ((lat - minLat) / span) * (height - 2 * padding);
  };

  const getTopSource = (s: StationData): SourceId => {
    const order: SourceId[] = ['traffic', 'industry', 'dust', 'biomass'];
    let topSrc: SourceId = 'traffic';
    let topVal = -1;
    for (const src of order) {
      const v = s.ugm3[src] || 0;
      if (v > topVal) {
        topVal = v;
        topSrc = src;
      }
    }
    return topSrc;
  };

  return (
    <div className="relative space-y-2">
      <div className="flex items-center justify-between text-xs text-slate-500 mb-2">
        <span>Delhi NCR Monitoring Grid</span>
        <span>Circle radius = PM₂.₅; Color = largest local source</span>
      </div>

      <div className="border border-slate-200/90 rounded-2xl overflow-hidden bg-slate-50/50 p-2">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="w-full h-auto max-h-[380px]"
          role="img"
          aria-label="Delhi Station Map"
        >
          {/* Subtle background grid */}
          <rect x={1} y={1} width={width - 2} height={height - 2} rx={16} fill="#f8fafc" />
          <line
            x1={padding}
            y1={height - padding}
            x2={width - padding}
            y2={height - padding}
            stroke="#e2e8f0"
            strokeDasharray="3 3"
          />
          <line
            x1={padding}
            y1={padding}
            x2={padding}
            y2={height - padding}
            stroke="#e2e8f0"
            strokeDasharray="3 3"
          />

          {validStations.map(s => {
            const cx = getX(s.lon as number);
            const cy = getY(s.lat as number);
            const topSrc = getTopSource(s);
            const radius = 6 + (s.observed_pm25 / Math.max(maxObs, 1)) * 14;
            const isSelected = selectedStation === s.station;

            return (
              <g
                key={s.station}
                className="cursor-pointer transition-transform duration-200"
                onClick={() => onSelectStation(isSelected ? null : s.station)}
                onMouseEnter={() => setHoveredStation(s)}
                onMouseLeave={() => setHoveredStation(null)}
              >
                {/* Highlight ring for selected station */}
                {isSelected && (
                  <circle
                    cx={cx}
                    cy={cy}
                    r={radius + 5}
                    fill="none"
                    stroke="#0f172a"
                    strokeWidth={2}
                    strokeDasharray="3 2"
                  />
                )}

                {/* Station bubble */}
                <circle
                  cx={cx}
                  cy={cy}
                  r={radius}
                  fill={SOURCE_COLORS[topSrc]}
                  opacity={isSelected ? 0.95 : 0.8}
                  stroke="#ffffff"
                  strokeWidth={2}
                  className="hover:scale-110 transition-transform origin-center"
                />

                {/* Station label */}
                <text
                  x={cx}
                  y={cy + radius + 12}
                  textAnchor="middle"
                  className="text-[10px] font-semibold fill-slate-700 pointer-events-none"
                >
                  {s.station.replace('Major Dhyan Chand Stadium', 'Dhyan Chand').replace(' Ph-2', '')}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      {/* Floating Info card on hover */}
      {hoveredStation && (
        <div className="absolute bottom-4 left-4 right-4 bg-slate-900/95 text-white p-3 rounded-xl shadow-xl text-xs flex items-center justify-between pointer-events-none">
          <div>
            <div className="font-bold text-slate-100">{hoveredStation.station}</div>
            <div className="text-[11px] text-slate-400">
              Top source: {SOURCE_NAMES[getTopSource(hoveredStation)]}
            </div>
          </div>
          <div className="text-right">
            <div className="font-black text-sm text-blue-300">
              {formatNumber(hoveredStation.observed_pm25, 0)} µg/m³
            </div>
            <div className="text-[10px] text-slate-400">observed PM₂.₅</div>
          </div>
        </div>
      )}
    </div>
  );
}
