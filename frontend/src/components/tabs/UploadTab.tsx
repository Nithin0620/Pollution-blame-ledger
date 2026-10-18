import { useState } from 'react';
import { Play } from 'lucide-react';
import { UploadValidationResult } from '../../types';
import { Card } from '../common/Card';
import { Dropzone } from '../upload/Dropzone';
import { ColumnDiagnosticTable } from '../upload/ColumnDiagnosticTable';
import { PreviewChart } from '../upload/PreviewChart';
import { uploadAndValidateCsv, startMcmcJob } from '../../api/client';

interface UploadTabProps {
  onJobStarted: (jobId: string) => void;
}

export function UploadTab({ onJobStarted }: UploadTabProps) {
  const [loading, setLoading] = useState(false);
  const [validationResult, setValidationResult] = useState<UploadValidationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [startingJob, setStartingJob] = useState(false);

  const handleFile = async (file: File) => {
    setLoading(true);
    setError(null);
    try {
      const res = await uploadAndValidateCsv(file);
      setValidationResult(res);
    } catch (err: any) {
      setError(err.message || 'Failed to parse CSV file');
    } finally {
      setLoading(false);
    }
  };

  const handleRunInference = async () => {
    if (!validationResult || !validationResult.valid) return;
    setStartingJob(true);
    try {
      const job = await startMcmcJob('uploaded_csv', { filename: validationResult.filename });
      onJobStarted(job.job_id);
    } catch (err: any) {
      setError(err.message || 'Failed to trigger MCMC job');
    } finally {
      setStartingJob(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h2 className="text-xl font-extrabold text-slate-900 tracking-tight">
          Upload & Validate Continuous Ambient Air Quality Data
        </h2>
        <p className="text-sm text-slate-500">
          Check your station CSV against the CPCB schema. The validator ensures all mandatory chemical tracers (PM₂.₅, PM₁₀, NO₂, SO₂, CO) and meteorology (WS, WD) exist before queuing full Bayesian receptor attribution.
        </p>
      </div>

      {/* Dropzone Card */}
      <Card className="p-6">
        <Dropzone onFileSelected={handleFile} isLoading={loading} />
      </Card>

      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs font-semibold">
          {error}
        </div>
      )}

      {/* Diagnostics and Preview */}
      {validationResult && (
        <Card className="p-6 space-y-6 animate-in fade-in duration-300">
          <ColumnDiagnosticTable result={validationResult} />

          {validationResult.preview_points.length > 0 && (
            <PreviewChart points={validationResult.preview_points} />
          )}

          {validationResult.valid && (
            <div className="pt-4 border-t border-slate-100 flex items-center justify-between">
              <div>
                <span className="text-xs font-bold text-slate-900">Run Source Apportionment</span>
                <p className="text-[11px] text-slate-500">
                  Runs NumPyro hierarchical Bayesian sampler asynchronously with background tracking.
                </p>
              </div>

              <button
                onClick={handleRunInference}
                disabled={startingJob}
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs shadow-md shadow-blue-500/20 disabled:opacity-50 transition-all"
              >
                {startingJob ? (
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <Play className="w-4 h-4 fill-white" />
                )}
                <span>Launch Attribution Model</span>
              </button>
            </div>
          )}
        </Card>
      )}
    </div>
  );
}
