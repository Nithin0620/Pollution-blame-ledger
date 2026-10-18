import { useState } from 'react';
import { Car, Factory, Wind, Flame, Cloud, ArrowRight } from 'lucide-react';
import { ComponentData, FlaggedPair } from '../../types';
import { Card } from '../common/Card';
import { Badge } from '../common/Badge';
import { SourceDetailDrawer } from '../sources/SourceDetailDrawer';
import { SOURCE_COLORS, SOURCE_NAMES, SourceId } from '../../utils/colors';
import { formatNumber, formatPercent, formatRange } from '../../utils/formatters';

interface SourcesTabProps {
  components: ComponentData[];
  flaggedPairs?: FlaggedPair[];
}

export function SourcesTab({ components, flaggedPairs = [] }: SourcesTabProps) {
  const [selectedSource, setSelectedSource] = useState<SourceId | null>(null);

  const icons: Record<SourceId, any> = {
    traffic: Car,
    industry: Factory,
    dust: Wind,
    biomass: Flame,
    background: Cloud,
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'identified':
        return <Badge variant="identified">Confident</Badge>;
      case 'weak':
        return <Badge variant="weak">Rough estimate</Badge>;
      case 'unresolved':
        return <Badge variant="unresolved">Collinear pair</Badge>;
      default:
        return <Badge variant="neutral">{status}</Badge>;
    }
  };

  const activeComp = components.find(c => c.id === selectedSource) || null;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <h2 className="text-xl font-extrabold text-slate-900 tracking-tight">
            Source-by-Source Breakdown
          </h2>
          <p className="text-sm text-slate-500">
            Estimated contribution of each of the 5 air pollution sources to Delhi's ambient PM₂.₅ smog.
          </p>
        </div>
      </div>

      {/* Grid of 5 Source Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {components.map(comp => {
          const id = comp.id as SourceId;
          const Icon = icons[id] || Wind;
          const color = SOURCE_COLORS[id];
          const name = SOURCE_NAMES[id];

          return (
            <Card
              key={id}
              hoverable
              onClick={() => setSelectedSource(id)}
              className="p-5 flex flex-col justify-between group"
            >
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2.5">
                    <div
                      className="w-8 h-8 rounded-xl flex items-center justify-center text-white shadow-sm"
                      style={{ backgroundColor: color }}
                    >
                      <Icon className="w-4 h-4" />
                    </div>
                    <span className="font-bold text-slate-900 text-sm">{name}</span>
                  </div>
                  {getStatusBadge(comp.status)}
                </div>

                <div className="space-y-1 mb-4">
                  <div className="flex items-baseline gap-2">
                    <span className="text-3xl font-black text-slate-900 tracking-tight">
                      {formatPercent(comp.share.mean)}
                    </span>
                    <span className="text-sm font-semibold text-slate-500">
                      ({formatNumber(comp.ugm3.mean, 0)} µg/m³)
                    </span>
                  </div>
                  <div className="text-xs text-slate-500">
                    90% range: {formatRange(comp.ugm3, 0)} µg/m³
                  </div>
                </div>
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs font-semibold text-blue-600 group-hover:text-blue-700">
                <span>View evidence & health data</span>
                <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover:translate-x-1" />
              </div>
            </Card>
          );
        })}
      </div>

      {/* Detail Slide-Over Drawer */}
      <SourceDetailDrawer
        sourceId={selectedSource}
        onClose={() => setSelectedSource(null)}
        component={activeComp}
        flaggedPairs={flaggedPairs}
      />
    </div>
  );
}
