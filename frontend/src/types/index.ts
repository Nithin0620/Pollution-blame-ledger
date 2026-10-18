export interface UncertaintyRange {
  mean: number;
  lo: number;
  hi: number;
}

export interface ComponentData {
  id: 'traffic' | 'industry' | 'dust' | 'biomass' | 'background';
  share: UncertaintyRange;
  ugm3: UncertaintyRange;
  mean_ugm3?: UncertaintyRange;
  status: 'identified' | 'weak' | 'unresolved';
  deaths_100?: UncertaintyRange;
  deaths_50?: UncertaintyRange;
  adm_100?: UncertaintyRange;
}

export interface FlaggedPair {
  a: string;
  b: string;
  correlation?: number;
  sum_ugm3: UncertaintyRange;
  sum_deaths_100?: UncertaintyRange;
}

export interface StationData {
  station: string;
  lat?: number;
  lon?: number;
  observed_pm25: number;
  background: number;
  ugm3: Record<string, number>;
}

export interface LiteratureRef {
  ref: string;
  low: number;
  high: number;
  overlaps: boolean;
}

export interface LiteratureComparisonItem {
  ours: UncertaintyRange;
  refs: LiteratureRef[];
}

export interface IdentifiabilityData {
  flagged_pairs: FlaggedPair[];
  names: string[];
  corr_matrix?: number[][];
  info_gain?: number[];
  rel_width?: number[];
  status?: Record<string, string>;
}

export interface DatasetResults {
  stations: string[];
  times: string[];
  episode_days: number;
  total_pm25: UncertaintyRange;
  total_deaths: UncertaintyRange;
  total_adm?: UncertaintyRange;
  components: ComponentData[];
  identifiability: IdentifiabilityData;
  hourly: Record<string, { mean: number[]; lo: number[]; hi: number[] }>;
  observed_pm25_popw: number[];
  by_station?: StationData[];
  literature?: Record<string, LiteratureComparisonItem>;
  data_source: 'synthetic' | 'observed';
  data_note?: string;
  health_assumptions?: {
    baseline_rate: number;
    adult_share: number;
    gemm: {
      theta: number;
      theta_se: number;
    };
    admissions: {
      rr_per10: number;
      base_rate: number;
    };
  };
}

export interface DatasetSummary {
  id: string;
  name: string;
  kind: 'synthetic' | 'real';
  total_pm25_mean: number;
  stations_count: number;
  dominant_source: string;
  dominant_source_share: number;
  description?: string;
}

export interface DatasetDetail {
  id: string;
  name: string;
  kind: 'synthetic' | 'real';
  results: DatasetResults;
  validation?: any;
}

export interface PolicyCuts {
  traffic: number;
  biomass: number;
  dust: number;
  industry: number;
}

export interface SourceAverted {
  source: string;
  averted_deaths: number;
}

export interface SimulationResult {
  original_pm25: number;
  new_pm25: number;
  absolute_reduction: number;
  percentage_reduction: number;
  who_guideline: number;
  original_who_multiplier: number;
  new_who_multiplier: number;
  averted_deaths_mean: number;
  averted_deaths_lo: number;
  averted_deaths_hi: number;
  averted_share_of_total: number;
  by_source: SourceAverted[];
  identifiability_warning?: string | null;
}

export interface JobStatus {
  job_id: string;
  status: 'queued' | 'running' | 'completed' | 'failed';
  progress_percent: number;
  current_stage: string;
  started_at: string;
  finished_at?: string | null;
  result_dataset_id?: string | null;
  error?: string | null;
}

export interface PreviewPoint {
  hour: number;
  pm25: number | null;
}

export interface UploadValidationResult {
  valid: boolean;
  filename: string;
  row_count: number;
  date_range?: string[];
  columns_present: string[];
  columns_missing: string[];
  columns_optional: string[];
  missing_percentage_pm25?: number;
  mean_pm25?: number;
  max_pm25?: number;
  preview_points: PreviewPoint[];
  message: string;
}
