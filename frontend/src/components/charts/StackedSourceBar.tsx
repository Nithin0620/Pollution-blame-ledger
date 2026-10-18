import { ComponentData } from '../../types';
import { SOURCE_COLORS, SOURCE_SHORT_NAMES, SourceId } from '../../utils/colors';
import { formatPercent } from '../../utils/formatters';

interface StackedSourceBarProps {
  components: ComponentData[];
  onSelectSource?: (sourceId: SourceId) => void;
  className?: string;
  showLabels?: boolean;
}

export function StackedSourceBar({
  components,
  onSelectSource,
  className = '',
  showLabels = true,
}: StackedSourceBarProps) {
  const orderedKeys: SourceId[] = ['traffic', 'industry', 'dust', 'biomass', 'background'];

  const parts = orderedKeys
    .map(key => {
      const comp = components.find(c => c.id === key);
      const share = comp ? comp.share.mean : 0;
      return {
        id: key,
        name: SOURCE_SHORT_NAMES[key],
        color: SOURCE_COLORS[key],
        share,
        percentage: Math.max(0, Math.min(100, share * 100)),
      };
    })
    .filter(p => p.percentage > 0);

  return (
    <div className={`space-y-3 ${className}`}>
      {/* The Bar */}
      <div className="flex h-5 w-full rounded-full overflow-hidden bg-slate-100 shadow-inner">
        {parts.map(part => (
          <div
            key={part.id}
            onClick={() => onSelectSource?.(part.id)}
            style={{
              width: `${part.percentage}%`,
              backgroundColor: part.color,
            }}
            className="h-full transition-all hover:opacity-90 cursor-pointer relative group"
            title={`${part.name}: ${formatPercent(part.share)}`}
          />
        ))}
      </div>

      {/* Legend / Labels below */}
      {showLabels && (
        <div className="flex flex-wrap items-center gap-x-6 gap-y-2 text-xs font-medium text-slate-600">
          {parts.map(part => (
            <button
              key={part.id}
              onClick={() => onSelectSource?.(part.id)}
              className="inline-flex items-center gap-1.5 hover:text-slate-900 transition-colors"
            >
              <span
                className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                style={{ backgroundColor: part.color }}
              />
              <span>{part.name}</span>
              <span className="font-bold text-slate-900">{formatPercent(part.share)}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
