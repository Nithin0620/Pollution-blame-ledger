import { ComponentData, PolicyCuts, SimulationResult, SourceAverted } from '../types';
import { WHO_24H_GUIDELINE } from './formatters';

export function calculateClientSimulation(
  components: ComponentData[],
  totalPm25Mean: number,
  totalDeathsMean: number,
  cuts: PolicyCuts,
  flaggedPairs: any[] = []
): SimulationResult {
  const sources: Array<keyof PolicyCuts> = ['traffic', 'biomass', 'dust', 'industry'];
  
  let avertedMean = 0;
  let avertedLo = 0;
  let avertedHi = 0;
  let pmReduction = 0;
  const bySource: SourceAverted[] = [];

  for (const src of sources) {
    const fraction = (cuts[src] || 0) / 100;
    const comp = components.find(c => c.id === src);
    if (!comp) continue;

    const d100 = comp.deaths_100 || { mean: 0, lo: 0, hi: 0 };
    const d50 = comp.deaths_50 || {
      mean: d100.mean * 0.5,
      lo: d100.lo * 0.5,
      hi: d100.hi * 0.5,
    };

    const calc = (val100: number, val50: number) => {
      return fraction <= 0.5
        ? val50 * (fraction / 0.5)
        : val50 + (val100 - val50) * ((fraction - 0.5) / 0.5);
    };

    const srcAvertedMean = calc(d100.mean, d50.mean);
    const srcAvertedLo = calc(d100.lo, d50.lo);
    const srcAvertedHi = calc(d100.hi, d50.hi);

    avertedMean += srcAvertedMean;
    avertedLo += srcAvertedLo;
    avertedHi += srcAvertedHi;

    const meanUgm3 = (comp.mean_ugm3 && comp.mean_ugm3.mean) || comp.ugm3.mean;
    pmReduction += meanUgm3 * fraction;

    bySource.push({
      source: src,
      averted_deaths: Math.round(srcAvertedMean * 10) / 10,
    });
  }

  const newPm25 = Math.max(0, totalPm25Mean - pmReduction);
  const absRed = totalPm25Mean - newPm25;
  const pctRed = totalPm25Mean > 0 ? (absRed / totalPm25Mean) * 100 : 0;

  // Warning check
  let warning: string | null = null;
  const tbPair = flaggedPairs.find(
    p => (p.a === 'traffic' && p.b === 'biomass') || (p.a === 'biomass' && p.b === 'traffic')
  );
  if (tbPair && (cuts.traffic > 0 !== cuts.biomass > 0)) {
    warning = "Vehicles and crop burning are partially collinear in this episode; treat individual numbers cautiously compared to their combined total.";
  }

  return {
    original_pm25: Math.round(totalPm25Mean * 10) / 10,
    new_pm25: Math.round(newPm25 * 10) / 10,
    absolute_reduction: Math.round(absRed * 10) / 10,
    percentage_reduction: Math.round(pctRed * 10) / 10,
    who_guideline: WHO_24H_GUIDELINE,
    original_who_multiplier: Math.round((totalPm25Mean / WHO_24H_GUIDELINE) * 10) / 10,
    new_who_multiplier: Math.round((newPm25 / WHO_24H_GUIDELINE) * 10) / 10,
    averted_deaths_mean: Math.round(avertedMean * 10) / 10,
    averted_deaths_lo: Math.round(avertedLo * 10) / 10,
    averted_deaths_hi: Math.round(avertedHi * 10) / 10,
    averted_share_of_total: totalDeathsMean > 0 ? Math.round((avertedMean / totalDeathsMean) * 1000) / 1000 : 0,
    by_source: bySource,
    identifiability_warning: warning,
  };
}
