import { useState } from 'react';
import { DatasetResults } from '../../types';
import { Card } from '../common/Card';
import { HourlyTimelineChart } from '../charts/HourlyTimelineChart';
import { HourlyDetailPanel } from '../charts/HourlyDetailPanel';

interface TimelineTabProps {
  results: DatasetResults;
}

export function TimelineTab({ results }: TimelineTabProps) {
  const [pinnedHour, setPinnedHour] = useState<number | null>(null);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-extrabold text-slate-900 tracking-tight">
          Hourly Smog Dynamics & Source Evolution
        </h2>
        <p className="text-sm text-slate-500">
          Track how each pollution component swells and fades hour by hour across Delhi NCR. Click the chart to freeze inspection at any hour.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Main Timeline Chart */}
        <Card className="p-6 lg:col-span-8">
          <HourlyTimelineChart
            results={results}
            pinnedHour={pinnedHour}
            onPinHour={setPinnedHour}
          />
        </Card>

        {/* Drill-down panel for the pinned or peak hour */}
        <div className="lg:col-span-4">
          <HourlyDetailPanel
            results={results}
            hourIndex={pinnedHour}
            onClearPin={() => setPinnedHour(null)}
          />
        </div>
      </div>
    </div>
  );
}
