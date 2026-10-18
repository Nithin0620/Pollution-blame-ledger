import { ComponentData, FlaggedPair } from '../../types';
import { Card } from '../common/Card';
import { Slider } from '../common/Slider';
import { BeforeAfterComparison } from '../simulator/BeforeAfterComparison';
import { useSimulation } from '../../hooks/useSimulation';
import { SOURCE_COLORS, SOURCE_NAMES } from '../../utils/colors';

interface WhatIfTabProps {
  components: ComponentData[];
  totalPm25Mean: number;
  totalDeathsMean: number;
  flaggedPairs?: FlaggedPair[];
}

export function WhatIfTab({
  components,
  totalPm25Mean,
  totalDeathsMean,
  flaggedPairs = [],
}: WhatIfTabProps) {
  const { cuts, updateCut, resetCuts, applyPreset, result } = useSimulation(
    components,
    totalPm25Mean,
    totalDeathsMean,
    flaggedPairs
  );

  const presets = [
    { label: 'Halve Vehicles', cuts: { traffic: 50 } },
    { label: 'Eliminate Crop Fires', cuts: { biomass: 100 } },
    { label: 'Halve Road Dust', cuts: { dust: 50 } },
    { label: '50% Cut Across All Sources', cuts: { traffic: 50, biomass: 50, dust: 50, industry: 50 } },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-extrabold text-slate-900 tracking-tight">
          What-If Policy Intervention Simulator
        </h2>
        <p className="text-sm text-slate-500">
          Simulate counterfactual clean air policies. Adjust source reduction sliders to evaluate averted premature deaths and ambient PM₂.₅ drop in real time.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Sliders Panel */}
        <Card className="p-6 space-y-6 lg:col-span-7">
          {/* Presets */}
          <div>
            <div className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2.5">
              Quick Policy Presets
            </div>
            <div className="flex flex-wrap gap-2">
              {presets.map(p => (
                <button
                  key={p.label}
                  onClick={() => applyPreset(p.cuts)}
                  className="px-3 py-1.5 rounded-xl text-xs font-bold bg-slate-100 hover:bg-slate-200/80 text-slate-800 transition-colors"
                >
                  {p.label}
                </button>
              ))}
              <button
                onClick={resetCuts}
                className="px-3 py-1.5 rounded-xl text-xs font-bold text-slate-500 hover:text-slate-800 transition-colors ml-auto"
              >
                Reset All
              </button>
            </div>
          </div>

          {/* Slider Controls */}
          <div className="space-y-5 pt-4 border-t border-slate-100">
            <Slider
              label={SOURCE_NAMES.traffic}
              value={cuts.traffic}
              onChange={v => updateCut('traffic', v)}
              color={SOURCE_COLORS.traffic}
            />
            <Slider
              label={SOURCE_NAMES.biomass}
              value={cuts.biomass}
              onChange={v => updateCut('biomass', v)}
              color={SOURCE_COLORS.biomass}
            />
            <Slider
              label={SOURCE_NAMES.dust}
              value={cuts.dust}
              onChange={v => updateCut('dust', v)}
              color={SOURCE_COLORS.dust}
            />
            <Slider
              label={SOURCE_NAMES.industry}
              value={cuts.industry}
              onChange={v => updateCut('industry', v)}
              color={SOURCE_COLORS.industry}
            />
          </div>

          <div className="pt-2 text-xs text-slate-500 leading-relaxed border-t border-slate-100">
            <span className="font-semibold text-slate-700">Methodology:</span> Evaluated via the non-linear GEMM concentration-response curve (Burnett et al. 2018) interpolating 50% and 100% Bayesian counterfactual posteriors.
          </div>
        </Card>

        {/* Results Panel */}
        <div className="lg:col-span-5">
          <BeforeAfterComparison result={result} />
        </div>
      </div>
    </div>
  );
}
