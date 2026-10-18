import { useState, useEffect } from 'react';
import { DatasetSummary, DatasetDetail } from '../types';
import { fetchDatasets, fetchDatasetDetail } from '../api/client';

export function useDataset(initialId?: string) {
  const [datasets, setDatasets] = useState<DatasetSummary[]>([]);
  const [selectedId, setSelectedId] = useState<string>(() => {
    return localStorage.getItem('pbl_dataset_id') || initialId || 'demo';
  });
  const [dataset, setDataset] = useState<DatasetDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // 1. Fetch all dataset summaries
  useEffect(() => {
    let mounted = true;
    fetchDatasets()
      .then(data => {
        if (mounted) {
          setDatasets(data);
          // If selectedId not in list and data exists, pick first
          if (data.length > 0 && !data.some(d => d.id === selectedId)) {
            setSelectedId(data[0].id);
          }
        }
      })
      .catch(err => {
        if (mounted) setError(err.message);
      });
    return () => { mounted = false; };
  }, []);

  // 2. Fetch specific dataset details when selectedId changes
  useEffect(() => {
    if (!selectedId) return;
    let mounted = true;
    setLoading(true);
    setError(null);

    fetchDatasetDetail(selectedId)
      .then(data => {
        if (mounted) {
          setDataset(data);
          setLoading(false);
          try {
            localStorage.setItem('pbl_dataset_id', selectedId);
          } catch (e) {}
        }
      })
      .catch(err => {
        if (mounted) {
          setError(err.message);
          setLoading(false);
        }
      });

    return () => { mounted = false; };
  }, [selectedId]);

  return {
    datasets,
    selectedId,
    setSelectedId,
    dataset,
    loading,
    error,
  };
}
