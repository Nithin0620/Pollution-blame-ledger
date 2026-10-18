import { Heart, Wind, AlertCircle } from 'lucide-react';
import { SimulationResult } from '../../types';
import { Card } from '../common/Card';
import { SOURCE_COLORS, SourceId } from '../../utils/colors';
import { formatNumber, formatPercent } from '../../utils/formatters';

interface BeforeAfterComparisonProps {
  result: SimulationResult;
}

export function BeforeAfterComparison({ result }: BeforeAfterComparisonProps) {
  const hasIntervention = result.averted_deaths_mean > 0 || result.absolute_reduction > 0;

  return (
    <Card className="p-6 space-y-6 bg-gradient-to-br from-white to-slate-50/50">
      {/* Primary KPI: Averted Deaths */}
      <div>
        <div className="flex items-center gap-2 text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">
          <Heart className="w-4 h-4 text-rose-500" />
          <span>Premature Deaths Avoided</span>
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-5xl font-black text-slate-900 tracking-tight">
            {hasIntervention ? `~${formatNumber(result.averted_deaths_mean, 0)}` : '0'}
          </span>
          <span className="text-sm font-semibold text-slate-500">lives saved</span>
        </div>

        <p className="text-xs text-slate-500 mt-1">
          {hasIntervention
            ? `Likely 90% range: ${formatNumber(result.averted_deaths_lo, 0)} – ${formatNumber(
                result.averted_deaths_hi,
                0
              )} lives (${formatPercent(result.averted_share_of_total)} of all episode deaths)`
            : 'Move the policy sliders to test an emission cut.'}
        </p>

        {/* Source Contribution Breakdown Bar */}
        {hasIntervention && result.by_source.length > 0 && (
          <div className="mt-3 flex h-3 w-full rounded-full overflow-hidden bg-slate-200">
            {result.by_source
              .filter(s => s.averted_deaths > 0)
              .map(s => {
                const pct = (s.averted_deaths / Math.max(result.averted_deaths_mean, 1)) * 100;
                return (
                  <div
                    key={s.source}
                    style={{
                      width: `${pct}%`,
                      backgroundColor: SOURCE_COLORS[s.source as SourceId],
                    }}
                    title={`${s.source}: ~${s.averted_deaths} deaths`}
                    className="h-full"
                  />
                );
              })}
          </div>
        )}
      </div>

      {/* Comparison Grid */}
      <div className="grid grid-cols-2 gap-4 pt-4 border-t border-slate-200/80">
        <div>
          <div className="flex items-center gap-1.5 text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">
            <Wind className="w-3.5 h-3.5 text-blue-500" />
            <span>New Average Smog</span>
          </div>
          <div className="text-2xl font-black text-slate-900">
            {formatNumber(result.new_pm25, 0)} <span className="text-xs font-normal">µg/m³</span>
          </div>
          <div className="text-xs text-slate-500">
            was {formatNumber(result.original_pm25, 0)} µg/m³{' '}
            {hasIntervention && (
              <span className="text-emerald-700 font-bold">
                (−{formatPercent(result.percentage_reduction / 100)})
              </span>
            )}
          </div>
        </div>

        <div>
          <div className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">
            WHO 24h Exceedance
          </div>
          <div className="text-2xl font-black text-slate-900">
            {result.new_who_multiplier}×
          </div>
          <div className="text-xs text-slate-500">
            was {result.original_who_multiplier}× standard limit ({result.who_guideline} µg/m³)
          </div>
        </div>
      </div>

      {/* Warning Box */}
      {result.identifiability_warning && (
        <div className="p-3.5 rounded-xl bg-amber-50 border border-amber-200/90 text-xs text-amber-900 flex items-start gap-2.5">
          <AlertCircle className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
          <div className="leading-relaxed">
            <span className="font-bold">Collinearity Caution:</span>{' '}
            {result.identifiability_warning}
          </div>
        </div>
      )}
    </Card>
  );
}
