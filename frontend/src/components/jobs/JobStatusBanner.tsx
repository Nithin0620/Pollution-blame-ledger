import { Loader2, CheckCircle2, AlertCircle, X } from 'lucide-react';
import { JobStatus } from '../../types';

interface JobStatusBannerProps {
  job: JobStatus | null;
  onDismiss: () => void;
  onViewDataset?: (datasetId: string) => void;
}

export function JobStatusBanner({ job, onDismiss, onViewDataset }: JobStatusBannerProps) {
  if (!job) return null;

  const isCompleted = job.status === 'completed';
  const isFailed = job.status === 'failed';
  const isRunning = job.status === 'running' || job.status === 'queued';

  return (
    <div className="fixed bottom-6 right-6 z-50 max-w-sm w-full bg-slate-900 text-white rounded-2xl shadow-2xl p-4 border border-slate-800 animate-in slide-in-from-bottom duration-300">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2.5">
          {isRunning && <Loader2 className="w-5 h-5 text-blue-400 animate-spin flex-shrink-0" />}
          {isCompleted && <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0" />}
          {isFailed && <AlertCircle className="w-5 h-5 text-rose-400 flex-shrink-0" />}

          <div>
            <div className="font-bold text-xs text-slate-100">
              {isRunning && 'Running Bayesian Receptor Model...'}
              {isCompleted && 'Attribution Model Complete!'}
              {isFailed && 'Attribution Run Failed'}
            </div>
            <div className="text-[11px] text-slate-400 mt-0.5 line-clamp-1">
              {job.current_stage || job.error}
            </div>
          </div>
        </div>

        <button
          onClick={onDismiss}
          className="text-slate-500 hover:text-slate-300 p-0.5 rounded-lg transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {isRunning && (
        <div className="mt-3 space-y-1">
          <div className="flex justify-between text-[10px] font-semibold text-slate-400">
            <span>Progress</span>
            <span>{job.progress_percent}%</span>
          </div>
          <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-500 transition-all duration-300"
              style={{ width: `${job.progress_percent}%` }}
            />
          </div>
        </div>
      )}

      {isCompleted && job.result_dataset_id && (
        <div className="mt-3 pt-2.5 border-t border-slate-800 flex justify-end">
          <button
            onClick={() => onViewDataset?.(job.result_dataset_id!)}
            className="text-xs font-bold text-blue-400 hover:text-blue-300"
          >
            Explore Generated Dataset &rarr;
          </button>
        </div>
      )}
    </div>
  );
}
