import React, { useState, useRef } from 'react';
import { UploadCloud, Download } from 'lucide-react';

interface DropzoneProps {
  onFileSelected: (file: File) => void;
  isLoading: boolean;
}

export function Dropzone({ onFileSelected, isLoading }: DropzoneProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      onFileSelected(e.dataTransfer.files[0]);
    }
  };

  const handleDownloadTemplate = (e: React.MouseEvent) => {
    e.stopPropagation();
    let rows = ['year,month,day,hour,PM2.5,PM10,NO2,SO2,CO,WS,WD,SR,AT'];
    for (let h = 0; h < 48; h++) {
      const hh = h % 24;
      const pm = (60 + 40 * Math.sin(h / 7) + 20 * (hh > 17 || hh < 6 ? 1 : 0)).toFixed(1);
      rows.push(
        `2025,11,${1 + Math.floor(h / 24)},${hh},${pm},${(Number(pm) * 2.1).toFixed(1)},${(
          20 +
          Number(pm) / 6
        ).toFixed(1)},${(8 + Number(pm) / 20).toFixed(1)},${(0.8 + Number(pm) / 80).toFixed(
          2
        )},${(1 + Math.max(0, Math.sin((hh - 6) / 4))).toFixed(2)},${(280 + h).toFixed(0)},${
          hh > 6 && hh < 18 ? 250 : 0
        },${(18 + 8 * Math.sin((hh - 9) / 4)).toFixed(1)}`
      );
    }
    const blob = new Blob([rows.join('\n')], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'cpcb_ledger_template.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div
      onDragOver={e => {
        e.preventDefault();
        setIsDragOver(true);
      }}
      onDragLeave={() => setIsDragOver(false)}
      onDrop={handleDrop}
      onClick={() => inputRef.current?.click()}
      className={`border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all ${
        isDragOver
          ? 'border-blue-500 bg-blue-50/60'
          : 'border-slate-300 hover:border-slate-400 bg-slate-50/50'
      }`}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".csv,.txt"
        onChange={e => {
          if (e.target.files && e.target.files.length > 0) {
            onFileSelected(e.target.files[0]);
          }
        }}
        className="hidden"
      />

      <div className="max-w-md mx-auto space-y-3">
        <div className="w-12 h-12 rounded-2xl bg-blue-100 text-blue-600 flex items-center justify-center mx-auto shadow-sm">
          {isLoading ? (
            <div className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
          ) : (
            <UploadCloud className="w-6 h-6" />
          )}
        </div>

        <div>
          <span className="font-extrabold text-sm text-slate-800">
            Click to upload your CPCB-format CSV
          </span>{' '}
          <span className="text-slate-500 text-sm">or drag and drop</span>
          <p className="text-xs text-slate-400 mt-1">
            Required columns: PM2.5, PM10, NO2, SO2, CO, WS, WD, year, month, day, hour
          </p>
        </div>

        <div className="pt-2">
          <button
            type="button"
            onClick={handleDownloadTemplate}
            className="inline-flex items-center gap-1.5 text-xs font-bold text-blue-600 hover:text-blue-800 hover:underline px-3 py-1 rounded-lg bg-blue-50 border border-blue-200/60 transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Download Sample CSV Template</span>
          </button>
        </div>
      </div>
    </div>
  );
}
