import { AlertTriangle, ShieldCheck, HeartPulse, Wind } from 'lucide-react';
import { DatasetDetail } from '../../types';
import { Card } from '../common/Card';
import { StackedSourceBar } from '../charts/StackedSourceBar';
import { SOURCE_NAMES, SourceId } from '../../utils/colors';
import { formatNumber, formatPercent, WHO_24H_GUIDELINE } from '../../utils/formatters';

interface DatasetHeroProps {
  dataset: DatasetDetail;
  onSelectSource?: (sourceId: SourceId) => void;
}

export function DatasetHero({ dataset, onSelectSource }: DatasetHeroProps) {
  const { results, kind } = dataset;
  const pmMean = results.total_pm25.mean;
  const whoMultiplier = (pmMean / WHO_24H_GUIDELINE).toFixed(1);
  const deathsMean = results.total_deaths.mean;

  // Find dominant source
  const topComp = results.components.slice().sort((a, b) => b.share.mean - a.share.mean)[0];
  const topSourceName = topComp ? SOURCE_NAMES[topComp.id] : 'Unknown';

  return (
    <section className="space-y-6">
      {/* Banner */}
      <div
        className={`px-4 py-3 rounded-2xl border text-xs sm:text-sm flex items-start gap-3 ${
          kind === 'synthetic'
            ? 'bg-amber-50/80 border-amber-200/80 text-amber-900'
            : 'bg-emerald-50/80 border-emerald-200/80 text-emerald-900'
        }`}
      >
        {kind === 'synthetic' ? (
          <AlertTriangle className="w-5 h-5 flex-shrink-0 text-amber-600 mt-0.5" />
        ) : (
          <ShieldCheck className="w-5 h-5 flex-shrink-0 text-emerald-600 mt-0.5" />
        )}
        <div className="leading-relaxed">
          <span className="font-bold">
            {kind === 'synthetic' ? 'Simulated Truth Dataset' : 'Observed Delhi Station Data'}:
          </span>{' '}
          {kind === 'synthetic'
            ? 'These readings are simulated with known ground truth to validate model recovery. Source shares have known answers.'
            : results.data_note ||
              'Real CPCB hourly station readings combined with NASA FIRMS active fire satellite detections.'}
        </div>
      </div>

      {/* Main KPI Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Metric 1: Average Smog */}
        <Card className="p-6">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-bold uppercase tracking-wider">Average PM₂.₅</span>
            <Wind className="w-4 h-4 text-blue-600" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-4xl font-black text-slate-900 tracking-tight">
              {formatNumber(pmMean, 0)}
            </span>
            <span className="text-sm font-semibold text-slate-500">µg/m³</span>
          </div>
          <div className="mt-2 text-xs font-semibold text-rose-600 bg-rose-50 px-2 py-0.5 rounded-md inline-block">
            {whoMultiplier}× above WHO 24h limit ({WHO_24H_GUIDELINE} µg/m³)
          </div>
        </Card>

        {/* Metric 2: Primary Offender */}
        <Card className="p-6">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-bold uppercase tracking-wider">Largest Contributor</span>
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500 animate-pulse" />
          </div>
          <div className="text-2xl font-black text-slate-900 tracking-tight truncate">
            {topSourceName}
          </div>
          <div className="mt-2 text-xs text-slate-600">
            Contributes <span className="font-bold text-slate-900">{formatPercent(topComp?.share.mean || 0)}</span> of total smog ({formatPercent(topComp?.share.lo || 0)} – {formatPercent(topComp?.share.hi || 0)} 90% range).
          </div>
        </Card>

        {/* Metric 3: Health Cost */}
        <Card className="p-6">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-bold uppercase tracking-wider">Episode Health Burden</span>
            <HeartPulse className="w-4 h-4 text-rose-600" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-4xl font-black text-slate-900 tracking-tight">
              ~{formatNumber(deathsMean, 0)}
            </span>
            <span className="text-sm font-semibold text-slate-500">equiv. deaths</span>
          </div>
          <div className="mt-2 text-xs text-slate-600">
            90% range: {formatNumber(results.total_deaths.lo, 0)} – {formatNumber(results.total_deaths.hi, 0)} (GEMM non-linear CRF).
          </div>
        </Card>
      </div>

      {/* Stacked Breakdown Card */}
      <Card className="p-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
          <div>
            <h3 className="text-base font-extrabold text-slate-900">Source Apportionment Distribution</h3>
            <p className="text-xs text-slate-500">
              Posterior mean contribution across {results.stations.length} Delhi stations over {results.episode_days} days.
            </p>
          </div>
          <span className="text-xs font-medium text-slate-400">Click any source segment for details</span>
        </div>
        <StackedSourceBar
          components={results.components}
          onSelectSource={onSelectSource}
        />
      </Card>
    </section>
  );
}
