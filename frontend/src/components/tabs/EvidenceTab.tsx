import { DatasetResults } from '../../types';
import { Card } from '../common/Card';
import { CredibleIntervalWhisker } from '../charts/CredibleIntervalWhisker';
import { IdentifiabilityHeatmap } from '../charts/IdentifiabilityHeatmap';
import { BaselinesTable } from '../evidence/BaselinesTable';
import { LiteratureComparison } from '../evidence/LiteratureComparison';

interface EvidenceTabProps {
  results: DatasetResults;
  validation?: any;
}

export function EvidenceTab({ results, validation }: EvidenceTabProps) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-extrabold text-slate-900 tracking-tight">
          Scientific Proof, Uncertainty & Model Validation
        </h2>
        <p className="text-sm text-slate-500">
          Transparent evidence backing our Bayesian source apportionment, including recovery of known ground truth, correlation diagnostics, and comparison with published literature.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Card 1: Ground Truth Recovery */}
        <Card className="p-6">
          <CredibleIntervalWhisker points={validation?.points || []} />
        </Card>

        {/* Card 2: Identifiability Heatmap */}
        <Card className="p-6">
          <IdentifiabilityHeatmap
            names={results.identifiability?.names || []}
            matrix={results.identifiability?.corr_matrix}
          />
        </Card>

        {/* Card 3: Baselines Comparison */}
        <Card className="p-6">
          <BaselinesTable
            baselines={validation?.baselines}
            shiftTest={validation?.shift_test}
          />
        </Card>

        {/* Card 4: Literature Comparison */}
        <Card className="p-6">
          <LiteratureComparison literature={results.literature} />
        </Card>
      </div>
    </div>
  );
}
