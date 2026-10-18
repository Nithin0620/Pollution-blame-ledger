import { useState } from 'react';
import { StationData } from '../../types';
import { Card } from '../common/Card';
import { StationScatterMap } from '../charts/StationScatterMap';
import { StationComparisonList } from '../charts/StationComparisonList';

interface StationsTabProps {
  stations: StationData[];
}

export function StationsTab({ stations }: StationsTabProps) {
  const [selectedStation, setSelectedStation] = useState<string | null>(null);

  if (!stations || stations.length === 0) {
    return (
      <Card className="p-8 text-center text-slate-500">
        No station-specific breakdown available for this single-receptor dataset.
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-extrabold text-slate-900 tracking-tight">
          Spatial Variation Across Delhi Monitoring Stations
        </h2>
        <p className="text-sm text-slate-500">
          Comparing the same pollution episode across CPCB monitoring stations. Traffic emissions concentrate near heavy arterial corridors while secondary background haze remains uniform.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Map Column */}
        <Card className="p-6 lg:col-span-7">
          <StationScatterMap
            stations={stations}
            selectedStation={selectedStation}
            onSelectStation={setSelectedStation}
          />
        </Card>

        {/* List Column */}
        <Card className="p-6 lg:col-span-5">
          <StationComparisonList
            stations={stations}
            selectedStation={selectedStation}
            onSelectStation={setSelectedStation}
          />
        </Card>
      </div>
    </div>
  );
}
