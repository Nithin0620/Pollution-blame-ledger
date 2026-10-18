import { Check, X, AlertCircle } from 'lucide-react';
import { UploadValidationResult } from '../../types';
import { formatNumber, WHO_24H_GUIDELINE } from '../../utils/formatters';

interface ColumnDiagnosticTableProps {
  result: UploadValidationResult;
}

export function ColumnDiagnosticTable({ result }: ColumnDiagnosticTableProps) {
  const requiredTracerColumns = ['PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'WS', 'WD'];

  return (
    <div className="space-y-4">
      {/* File Stats Summary */}
      <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div>
          <span className="font-bold text-slate-800 text-sm">{result.filename}</span>
          <span className="text-slate-500 ml-2">({formatNumber(result.row_count, 0)} hours)</span>
        </div>
        {result.mean_pm25 !== null && result.mean_pm25 !== undefined && (
          <div className="flex items-center gap-4 text-slate-600 font-medium">
            <span>
              Mean PM₂.₅:{' '}
              <span className="font-bold text-slate-900">{formatNumber(result.mean_pm25, 1)} µg/m³</span>{' '}
              ({(result.mean_pm25 / WHO_24H_GUIDELINE).toFixed(1)}× WHO limit)
            </span>
            {result.missing_percentage_pm25 !== null && result.missing_percentage_pm25 !== undefined && (
              <span>
                Missing: <span className="font-bold text-slate-900">{result.missing_percentage_pm25}%</span>
              </span>
            )}
          </div>
        )}
      </div>

      {/* Column Chips */}
      <div>
        <div className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
          Required Tracers & Meteorology
        </div>
        <div className="flex flex-wrap gap-2">
          {requiredTracerColumns.map(col => {
            const isPresent = result.columns_present.includes(col);
            return (
              <div
                key={col}
                className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-bold border ${
                  isPresent
                    ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                    : 'bg-rose-50 text-rose-800 border-rose-200'
                }`}
              >
                {isPresent ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <X className="w-3.5 h-3.5 text-rose-600" />}
                <span>{col}</span>
              </div>
            );
          })}

          {/* Optional Columns */}
          {['SR', 'AT'].map(col => {
            const isPresent = result.columns_optional.includes(col);
            return (
              <div
                key={col}
                className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-medium border ${
                  isPresent
                    ? 'bg-slate-100 text-slate-700 border-slate-300'
                    : 'bg-slate-50 text-slate-400 border-slate-200'
                }`}
              >
                <span>{col} (optional)</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Message Banner */}
      <div
        className={`p-3.5 rounded-xl border text-xs flex items-start gap-2.5 ${
          result.valid
            ? 'bg-emerald-50 border-emerald-200 text-emerald-900'
            : 'bg-rose-50 border-rose-200 text-rose-900'
        }`}
      >
        <AlertCircle className={`w-4 h-4 flex-shrink-0 mt-0.5 ${result.valid ? 'text-emerald-600' : 'text-rose-600'}`} />
        <div className="leading-relaxed">
          <span className="font-bold">{result.valid ? 'Ready for Attribution:' : 'Schema Issue:'}</span>{' '}
          {result.message}
        </div>
      </div>
    </div>
  );
}
