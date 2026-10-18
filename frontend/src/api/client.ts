import { DatasetSummary, DatasetDetail, PolicyCuts, SimulationResult, JobStatus, UploadValidationResult } from '../types';

const API_BASE = '/api';

export async function fetchDatasets(): Promise<DatasetSummary[]> {
  const res = await fetch(`${API_BASE}/datasets`);
  if (!res.ok) throw new Error(`Failed to fetch datasets: ${res.statusText}`);
  return res.json();
}

export async function fetchDatasetDetail(id: string): Promise<DatasetDetail> {
  const res = await fetch(`${API_BASE}/datasets/${id}`);
  if (!res.ok) throw new Error(`Failed to fetch dataset ${id}: ${res.statusText}`);
  return res.json();
}

export async function simulateInterventions(datasetId: string, cuts: PolicyCuts): Promise<SimulationResult> {
  const res = await fetch(`${API_BASE}/simulate/interventions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ dataset_id: datasetId, cuts }),
  });
  if (!res.ok) throw new Error(`Failed to simulate: ${res.statusText}`);
  return res.json();
}

export async function uploadAndValidateCsv(file: File): Promise<UploadValidationResult> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/upload/validate`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error(`Failed to validate file: ${res.statusText}`);
  return res.json();
}

export async function startMcmcJob(type: string = 'demo', config: Record<string, any> = {}): Promise<JobStatus> {
  const res = await fetch(`${API_BASE}/jobs/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ type, config }),
  });
  if (!res.ok) throw new Error(`Failed to start job: ${res.statusText}`);
  return res.json();
}

export async function pollJobStatus(jobId: string): Promise<JobStatus> {
  const res = await fetch(`${API_BASE}/jobs/${jobId}`);
  if (!res.ok) throw new Error(`Failed to poll job ${jobId}: ${res.statusText}`);
  return res.json();
}
