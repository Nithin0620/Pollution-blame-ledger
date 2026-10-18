import { ComponentData, FlaggedPair } from '../../types';
import { Drawer } from '../common/Drawer';
import { Badge } from '../common/Badge';
import { SOURCE_COLORS, SOURCE_NAMES, SOURCE_DESCRIPTIONS, SourceId } from '../../utils/colors';
import { formatNumber, formatPercent, formatRange } from '../../utils/formatters';

interface SourceDetailDrawerProps {
  sourceId: SourceId | null;
  onClose: () => void;
  component: ComponentData | null;
  flaggedPairs?: FlaggedPair[];
}

export function SourceDetailDrawer({
  sourceId,
  onClose,
  component,
  flaggedPairs = [],
}: SourceDetailDrawerProps) {
  if (!sourceId || !component) return null;

  const color = SOURCE_COLORS[sourceId];
  const name = SOURCE_NAMES[sourceId];
  const desc = SOURCE_DESCRIPTIONS[sourceId];

  // Identifiability partner check
  const pair = flaggedPairs.find(p => p.a === sourceId || p.b === sourceId);
  const partnerId = pair ? (pair.a === sourceId ? pair.b : pair.a) : null;
  const partnerName = partnerId ? SOURCE_NAMES[partnerId as SourceId] : null;

  const statusMap = {
    identified: {
      label: 'Identified (Confident)',
      variant: 'identified' as const,
      text: 'The uncertainty range is narrow and this source signature held up against synthetic and held-out validation.',
    },
    weak: {
      label: 'Rough Estimate',
      variant: 'weak' as const,
      text: 'The range is relatively wide; treat this value as an indicative ballpark rather than a pinpoint measurement.',
    },
    unresolved: {
      label: 'Collinear (Joint Sum Only)',
      variant: 'unresolved' as const,
      text: `The observation data cannot reliably separate ${name.toLowerCase()} from ${partnerName?.toLowerCase() || 'another source'}. Only their combined sum is constrained.`,
    },
  };

  const statusInfo = statusMap[component.status] || statusMap.identified;

  return (
    <Drawer isOpen={!!sourceId} onClose={onClose} title={name}>
      {/* Overview & Color Tag */}
      <div className="flex items-start gap-3">
        <div
          className="w-4 h-12 rounded-full flex-shrink-0"
          style={{ backgroundColor: color }}
        />
        <div>
          <Badge variant={statusInfo.variant} className="mb-2">
            {statusInfo.label}
          </Badge>
          <p className="text-sm text-slate-700 leading-relaxed">{desc}</p>
        </div>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-2 gap-3 pt-2">
        <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
          <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">
            Share of PM₂.₅
          </div>
          <div className="text-2xl font-black text-slate-900 mt-1">
            {formatPercent(component.share.mean)}
          </div>
          <div className="text-xs text-slate-500 mt-0.5">
            90% range: {formatPercent(component.share.lo)} – {formatPercent(component.share.hi)}
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
          <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">
            Contribution
          </div>
          <div className="text-2xl font-black text-slate-900 mt-1">
            {formatNumber(component.ugm3.mean, 1)} <span className="text-xs font-normal">µg/m³</span>
          </div>
          <div className="text-xs text-slate-500 mt-0.5">
            90% range: {formatRange(component.ugm3, 1)}
          </div>
        </div>
      </div>

      {/* Health Impact */}
      {component.deaths_100 && (
        <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
          <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">
            Attributable Premature Deaths (100% Counterfactual)
          </div>
          <div className="text-xl font-bold text-slate-900">
            ~{formatNumber(component.deaths_100.mean, 0)} lives
          </div>
          <div className="text-xs text-slate-500">
            90% credible interval: {formatRange(component.deaths_100, 0)} adult deaths during this episode length.
          </div>
        </div>
      )}

      {/* Identifiability & Collinearity Explanation */}
      <div className="p-4 rounded-xl border border-slate-200/90 bg-white space-y-2">
        <div className="text-xs font-bold text-slate-900 uppercase tracking-wider">
          Identifiability & Uncertainty Diagnostic
        </div>
        <p className="text-xs text-slate-600 leading-relaxed">{statusInfo.text}</p>
        {pair && (
          <div className="text-xs font-semibold text-rose-700 bg-rose-50 p-2.5 rounded-lg border border-rose-100">
            Collinear pair combined total: {formatNumber(pair.sum_ugm3.mean, 0)} µg/m³ ({formatRange(pair.sum_ugm3, 0)}).
          </div>
        )}
      </div>
    </Drawer>
  );
}
