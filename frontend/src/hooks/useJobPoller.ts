import { useState, useEffect, useRef } from 'react';
import { JobStatus } from '../types';
import { pollJobStatus } from '../api/client';

export function useJobPoller(activeJobId: string | null, onComplete?: (datasetId: string) => void) {
  const [job, setJob] = useState<JobStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const onCompleteRef = useRef(onComplete);
  onCompleteRef.current = onComplete;

  useEffect(() => {
    if (!activeJobId) {
      setJob(null);
      return;
    }

    let interval: any = null;
    let stopped = false;

    const check = async () => {
      try {
        const data = await pollJobStatus(activeJobId);
        if (stopped) return;
        setJob(data);

        if (data.status === 'completed' || data.status === 'failed') {
          clearInterval(interval);
          if (data.status === 'completed' && data.result_dataset_id && onCompleteRef.current) {
            onCompleteRef.current(data.result_dataset_id);
          }
        }
      } catch (err: any) {
        if (!stopped) setError(err.message);
      }
    };

    check();
    interval = setInterval(check, 1500);

    return () => {
      stopped = true;
      clearInterval(interval);
    };
  }, [activeJobId]);

  return { job, error };
}
