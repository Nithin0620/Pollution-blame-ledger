import { useState, useMemo } from 'react';
import { ComponentData, PolicyCuts, SimulationResult } from '../types';
import { calculateClientSimulation } from '../utils/gemm';

const DEFAULT_CUTS: PolicyCuts = {
  traffic: 0,
  biomass: 0,
  dust: 0,
  industry: 0,
};

export function useSimulation(
  components: ComponentData[],
  totalPm25Mean: number,
  totalDeathsMean: number,
  flaggedPairs: any[] = []
) {
  const [cuts, setCuts] = useState<PolicyCuts>(DEFAULT_CUTS);

  const updateCut = (source: keyof PolicyCuts, value: number) => {
    setCuts(prev => ({ ...prev, [source]: value }));
  };

  const resetCuts = () => {
    setCuts(DEFAULT_CUTS);
  };

  const applyPreset = (presetCuts: Partial<PolicyCuts>) => {
    setCuts({
      traffic: presetCuts.traffic || 0,
      biomass: presetCuts.biomass || 0,
      dust: presetCuts.dust || 0,
      industry: presetCuts.industry || 0,
    });
  };

  const result: SimulationResult = useMemo(() => {
    return calculateClientSimulation(
      components,
      totalPm25Mean,
      totalDeathsMean,
      cuts,
      flaggedPairs
    );
  }, [components, totalPm25Mean, totalDeathsMean, cuts, flaggedPairs]);

  return {
    cuts,
    updateCut,
    resetCuts,
    applyPreset,
    result,
  };
}
