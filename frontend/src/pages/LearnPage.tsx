import { Card } from '../components/common/Card';
import { BookOpen, ShieldAlert, FileText } from 'lucide-react';

export function LearnPage() {
  const steps = [
    {
      num: 1,
      title: 'Chemical Tracer Fingerprinting',
      desc: 'Ambient sensors do not measure "traffic" directly — they record chemical compounds. We isolate vehicles via CO & NO₂, industrial boilers via SO₂, coarse dust through the PM₁₀ surplus over PM₂.₅, and agricultural fires through NASA VIIRS satellite thermal anomaly FRP.',
    },
    {
      num: 2,
      title: 'Meteorological Dispersion Conditioning',
      desc: 'Wind speed, wind direction, planetary boundary layer height, and temperature determine how plumes dilute. Calm winds trap local vehicular emissions, while northwesterly winds transport biomass plumes across Punjab and Haryana into Delhi.',
    },
    {
      num: 3,
      title: 'Hierarchical Bayesian Receptor Modeling (NumPyro)',
      desc: 'Rather than assuming fixed source ratios, our model runs No-U-Turn Sampler (NUTS) MCMC in JAX to explore the full joint posterior distribution over thousands of Markov chain states, computing authentic credible intervals.',
    },
    {
      num: 4,
      title: 'Identifiability & Collinearity Diagnostic',
      desc: 'When two sources rise and fall together (e.g. traffic and crop burning during stagnant evening inversions), independent point estimation is false precision. We detect strong negative posterior correlation and report their robust joint sum.',
    },
    {
      num: 5,
      title: 'GEMM Non-Linear Health Burden Propagation',
      desc: 'Attributable premature mortality is calculated via Burnett et al. (2018) Global Exposure Mortality Model (GEMM). Because the concentration-response curve saturates at high pollution levels, cutting smog during peak days yields disproportionate health gains.',
    },
  ];

  return (
    <div className="space-y-8 max-w-4xl mx-auto py-4">
      <div>
        <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2.5">
          <BookOpen className="w-6 h-6 text-blue-600" />
          <span>How the Pollution Blame Ledger Works</span>
        </h1>
        <p className="text-sm text-slate-600 mt-1 leading-relaxed">
          The research methodology, Bayesian statistical engine, and non-linear concentration-response health modeling behind our source apportionment.
        </p>
      </div>

      {/* 5 Steps */}
      <div className="space-y-4">
        <h2 className="text-base font-extrabold text-slate-900 uppercase tracking-wider text-xs">
          The 5-Step Prediction Pipeline
        </h2>
        <div className="grid grid-cols-1 gap-4">
          {steps.map(s => (
            <Card key={s.num} className="p-5 flex items-start gap-4">
              <div className="w-9 h-9 rounded-xl bg-blue-600 text-white font-black text-sm flex items-center justify-center flex-shrink-0 shadow-md shadow-blue-500/20">
                {s.num}
              </div>
              <div className="space-y-1">
                <h3 className="font-bold text-slate-900 text-sm">{s.title}</h3>
                <p className="text-xs text-slate-600 leading-relaxed">{s.desc}</p>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* Health Model Explanation */}
      <Card className="p-6 space-y-3 bg-gradient-to-br from-white to-slate-50">
        <h3 className="text-sm font-extrabold text-slate-900 flex items-center gap-2">
          <FileText className="w-4 h-4 text-blue-600" />
          <span>GEMM Health Formulation</span>
        </h3>
        <p className="text-xs text-slate-600 leading-relaxed">
          We use the Global Exposure Mortality Model (Burnett et al. 2018, PNAS 115(38)) parameterized with θ = 0.1430 (SE 0.01807), α = 1.6, μ = 15.5, ν = 36.8, and theoretical counterfactual threshold 2.4 µg/m³.
        </p>
        <p className="text-xs text-slate-500 italic">
          Note: Episode-equivalent deaths express relative burden across sources scaled by episode duration / 365, rather than an immediate mortality head count during the event.
        </p>
      </Card>

      {/* Honest Limitations */}
      <Card className="p-6 space-y-3 border-amber-200/80 bg-amber-50/40">
        <h3 className="text-sm font-extrabold text-amber-900 flex items-center gap-2">
          <ShieldAlert className="w-4 h-4 text-amber-600" />
          <span>Known Limitations & Honest Bounds</span>
        </h3>
        <ul className="text-xs text-amber-950 space-y-2 list-disc list-inside leading-relaxed">
          <li>
            <b>Ground truth gap:</b> Real ambient air has no continuous chemical speciation ground truth; we validate against independent NASA satellite fire detection shifts and published inventory studies.
          </li>
          <li>
            <b>Collinear sources:</b> On windless winter nights, surface vehicle exhaust and burning plumes trap simultaneously; in such hours, only their joint sum should be cited.
          </li>
        </ul>
      </Card>
    </div>
  );
}
