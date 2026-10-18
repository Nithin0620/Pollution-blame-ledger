import { useState } from 'react';
import { Navbar } from './components/layout/Navbar';
import { DatasetHero } from './components/layout/DatasetHero';
import { SourcesTab } from './components/tabs/SourcesTab';
import { WhatIfTab } from './components/tabs/WhatIfTab';
import { TimelineTab } from './components/tabs/TimelineTab';
import { StationsTab } from './components/tabs/StationsTab';
import { EvidenceTab } from './components/tabs/EvidenceTab';
import { UploadTab } from './components/tabs/UploadTab';
import { LearnPage } from './pages/LearnPage';
import { JobStatusBanner } from './components/jobs/JobStatusBanner';
import { useDataset } from './hooks/useDataset';
import { useJobPoller } from './hooks/useJobPoller';
import { Layers, Sliders, Clock, MapPin, CheckCircle2 } from 'lucide-react';
import { SourceId } from './utils/colors';

export default function App() {
  const { datasets, selectedId, setSelectedId, dataset, loading, error } = useDataset();
  const [activeView, setActiveView] = useState<'dashboard' | 'learn' | 'upload'>('dashboard');
  const [activeTab, setActiveTab] = useState<'sources' | 'whatif' | 'timeline' | 'stations' | 'evidence'>('sources');
  const [activeJobId, setActiveJobId] = useState<string | null>(null);

  const { job } = useJobPoller(activeJobId, (newDatasetId) => {
    setSelectedId(newDatasetId);
    setActiveView('dashboard');
  });

  const tabs = [
    { id: 'sources', label: 'Sources', icon: Layers },
    { id: 'whatif', label: 'What If?', icon: Sliders },
    { id: 'timeline', label: 'Timeline', icon: Clock },
    { id: 'stations', label: 'Stations', icon: MapPin },
    { id: 'evidence', label: 'Evidence & Proof', icon: CheckCircle2 },
  ];

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans">
      {/* Navigation */}
      <Navbar
        datasets={datasets}
        selectedId={selectedId}
        onSelectDataset={setSelectedId}
        activeView={activeView}
        onNavigate={v => setActiveView(v as any)}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Error Notification */}
        {error && (
          <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 text-xs font-semibold">
            {error}
          </div>
        )}

        {/* View 1: Learn Page */}
        {activeView === 'learn' && <LearnPage />}

        {/* View 2: Upload Page */}
        {activeView === 'upload' && (
          <UploadTab
            onJobStarted={jobId => {
              setActiveJobId(jobId);
            }}
          />
        )}

        {/* View 3: Dashboard */}
        {activeView === 'dashboard' && (
          <>
            {loading && !dataset ? (
              <div className="py-24 text-center space-y-3">
                <div className="w-8 h-8 border-3 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto" />
                <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                  Loading Bayesian Model Posteriors...
                </p>
              </div>
            ) : dataset ? (
              <>
                {/* Hero Section */}
                <DatasetHero
                  dataset={dataset}
                  onSelectSource={(_sourceId: SourceId) => {
                    setActiveTab('sources');
                    const el = document.getElementById('tabs-section');
                    el?.scrollIntoView({ behavior: 'smooth' });
                  }}
                />

                {/* Tabs Navigation */}
                <div id="tabs-section" className="space-y-6 pt-4">
                  <div className="flex items-center gap-1.5 border-b border-slate-200 overflow-x-auto pb-px">
                    {tabs.map(tab => {
                      const Icon = tab.icon;
                      const isActive = activeTab === tab.id;
                      return (
                        <button
                          key={tab.id}
                          onClick={() => setActiveTab(tab.id as any)}
                          className={`flex items-center gap-2 px-4 py-3 text-xs font-bold border-b-2 transition-all whitespace-nowrap ${
                            isActive
                              ? 'border-blue-600 text-blue-600'
                              : 'border-transparent text-slate-500 hover:text-slate-800 hover:border-slate-300'
                          }`}
                        >
                          <Icon className="w-4 h-4" />
                          <span>{tab.label}</span>
                        </button>
                      );
                    })}
                  </div>

                  {/* Active Tab Panel */}
                  <div className="pt-2">
                    {activeTab === 'sources' && (
                      <SourcesTab
                        components={dataset.results.components}
                        flaggedPairs={dataset.results.identifiability?.flagged_pairs}
                      />
                    )}

                    {activeTab === 'whatif' && (
                      <WhatIfTab
                        components={dataset.results.components}
                        totalPm25Mean={dataset.results.total_pm25.mean}
                        totalDeathsMean={dataset.results.total_deaths.mean}
                        flaggedPairs={dataset.results.identifiability?.flagged_pairs}
                      />
                    )}

                    {activeTab === 'timeline' && (
                      <TimelineTab results={dataset.results} />
                    )}

                    {activeTab === 'stations' && (
                      <StationsTab stations={dataset.results.by_station || []} />
                    )}

                    {activeTab === 'evidence' && (
                      <EvidenceTab
                        results={dataset.results}
                        validation={dataset.validation}
                      />
                    )}
                  </div>
                </div>
              </>
            ) : null}
          </>
        )}
      </main>

      {/* Floating Background Job Banner */}
      <JobStatusBanner
        job={job}
        onDismiss={() => setActiveJobId(null)}
        onViewDataset={id => {
          setSelectedId(id);
          setActiveJobId(null);
        }}
      />

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white py-6 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-xs text-slate-500 space-y-1">
          <div>
            <b>Pollution Blame Ledger</b> &middot; Research Prototype &middot; Bayesian Hierarchical Source Apportionment
          </div>
          <div className="text-[11px] text-slate-400">
            CPCB Station Data &middot; NASA VIIRS FIRMS Active Fire Satellite &middot; GEMM Mortality Curve (Burnett et al. 2018)
          </div>
        </div>
      </footer>
    </div>
  );
}
