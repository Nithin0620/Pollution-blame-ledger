# Full-Stack React & FastAPI Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task inline. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a modern, editorial, full-stack React + FastAPI web application to replace the single-file HTML dashboard, integrating cleanly with the existing Python Bayesian modeling engine.

**Architecture:**
- **Backend**: FastAPI REST server (`backend/app/`) exposing `/api/datasets`, `/api/simulate`, `/api/upload`, and `/api/jobs` without modifying existing `ledger/` modeling code.
- **Frontend**: Vite + React 19 + TypeScript + Tailwind CSS SPA (`frontend/`) with Recharts and custom SVG charts, providing instant 60fps policy simulation, deep-dive drawers, and clean multi-tab layout.

**Tech Stack:**
- Python 3.12, FastAPI, Pydantic v2, Uvicorn, httpx, pytest
- Node.js, Vite, React 19, TypeScript, Tailwind CSS, Lucide React, Recharts

**Spec:** `docs/superpowers/specs/2026-10-18-react-fullstack-dashboard-design.md`

## Global Constraints
- Do NOT alter or rewrite existing modeling logic in `ledger/`.
- Preserve source palette: Vehicles (`#2563eb`), Factories (`#8b5cf6`), Dust (`#f59e0b`), Burning (`#ef4444`), Haze (`#94a3b8`).
- Maintain exact GEMM non-linear concentration-response formula from Burnett et al. (2018).
- Keep all tasks independently testable with TDD/verification steps.

---

### Task 1: FastAPI Backend Schemas, Config & Dataset Service

**Files:**
- Create: `backend/app/config.py`
- Create: `backend/app/schemas/dataset.py`
- Create: `backend/app/routers/datasets.py`
- Test: `backend/tests/test_datasets_api.py`

**Interfaces:**
- Produces: `GET /api/datasets`, `GET /api/datasets/{dataset_id}`

- [ ] **Step 1: Write the failing test for datasets endpoint**
- [ ] **Step 2: Run test to verify it fails**
- [ ] **Step 3: Implement config, dataset schemas, and datasets router reading outputs/**
- [ ] **Step 4: Run test to verify it passes**
- [ ] **Step 5: Commit**

---

### Task 2: FastAPI Policy Simulation, CSV Upload & Async Jobs Routers

**Files:**
- Create: `backend/app/schemas/simulation.py`
- Create: `backend/app/schemas/upload.py`
- Create: `backend/app/schemas/job.py`
- Create: `backend/app/routers/simulate.py`
- Create: `backend/app/routers/upload.py`
- Create: `backend/app/routers/jobs.py`
- Create: `backend/app/services/job_runner.py`
- Test: `backend/tests/test_simulate_upload_jobs_api.py`

**Interfaces:**
- Produces: `POST /api/simulate/interventions`, `POST /api/upload/validate`, `POST /api/jobs/run`, `GET /api/jobs/{job_id}`

- [ ] **Step 1: Write tests for simulate, upload validation, and job status**
- [ ] **Step 2: Run test to verify it fails**
- [ ] **Step 3: Implement simulation logic, CSV parsing, job runner, and routers**
- [ ] **Step 4: Run test to verify it passes**
- [ ] **Step 5: Commit**

---

### Task 3: FastAPI Application Setup & Integration Smoke Test

**Files:**
- Create: `backend/app/main.py`
- Create: `backend/requirements.txt`
- Test: `backend/tests/test_integration.py`

**Interfaces:**
- Produces: Root FastAPI app with CORS middleware, router aggregation, and `/health`

- [ ] **Step 1: Write integration test verifying OpenAPI docs and router aggregation**
- [ ] **Step 2: Implement `backend/app/main.py` and requirements**
- [ ] **Step 3: Run pytest on all backend tests**
- [ ] **Step 4: Commit**

---

### Task 4: Frontend Scaffolding with Vite, React, TypeScript & Tailwind CSS

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tsconfig.json`
- Create: `frontend/index.html`
- Create: `frontend/src/index.css`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx`

**Interfaces:**
- Produces: Running Vite dev environment with Tailwind CSS and Lucide React

- [ ] **Step 1: Scaffold package.json and vite config with dependencies**
- [ ] **Step 2: Run npm install**
- [ ] **Step 3: Setup index.html, Tailwind CSS classes, and basic App shell**
- [ ] **Step 4: Run npm build to verify clean bundling**
- [ ] **Step 5: Commit**

---

### Task 5: Frontend API Client, Types, and State Management Hooks

**Files:**
- Create: `frontend/src/types/index.ts`
- Create: `frontend/src/api/client.ts`
- Create: `frontend/src/hooks/useDataset.ts`
- Create: `frontend/src/hooks/useSimulation.ts`
- Create: `frontend/src/hooks/useJobPoller.ts`
- Create: `frontend/src/utils/colors.ts`
- Create: `frontend/src/utils/formatters.ts`
- Create: `frontend/src/utils/gemm.ts`

**Interfaces:**
- Produces: Type-safe client and reactive hooks for datasets, policy simulation, and health calculation

- [ ] **Step 1: Define TypeScript schemas matching FastAPI Pydantic models**
- [ ] **Step 2: Implement API client with error handling and fallback**
- [ ] **Step 3: Implement GEMM calculation utility with Burnett et al. parameters**
- [ ] **Step 4: Implement useDataset and useSimulation hooks**
- [ ] **Step 5: Verify types with `npx tsc --noEmit` and commit**

---

### Task 6: Visual Layout Primitives & Executive Summary Hero

**Files:**
- Create: `frontend/src/components/layout/Navbar.tsx`
- Create: `frontend/src/components/layout/DatasetHero.tsx`
- Create: `frontend/src/components/charts/StackedSourceBar.tsx`
- Create: `frontend/src/components/common/Badge.tsx`
- Create: `frontend/src/components/common/Card.tsx`
- Modify: `frontend/src/App.tsx`

**Interfaces:**
- Produces: Header navigation with dataset selector, Hero KPI cards, and interactive stacked source distribution bar

- [ ] **Step 1: Build Badge and Card UI primitives**
- [ ] **Step 2: Build Navbar with dataset switcher dropdown**
- [ ] **Step 3: Build DatasetHero with mean PM2.5, WHO multiplier, and attributable deaths**
- [ ] **Step 4: Build StackedSourceBar with hover tooltips**
- [ ] **Step 5: Verify build with `npx tsc --noEmit` and commit**

---

### Task 7: Sources Tab & Slide-Over Source Detail Drawer

**Files:**
- Create: `frontend/src/components/tabs/SourcesTab.tsx`
- Create: `frontend/src/components/common/Drawer.tsx`
- Create: `frontend/src/components/sources/SourceDetailDrawer.tsx`

**Interfaces:**
- Produces: 5-card source grid showing percentage shares, credible intervals, and deep-dive drawer for tracer evidence

- [ ] **Step 1: Build slide-over Drawer component with keyboard/backdrop dismiss**
- [ ] **Step 2: Build SourcesTab cards showing share %, 90% range, and status badges**
- [ ] **Step 3: Build SourceDetailDrawer showing chemical tracers and identifiability**
- [ ] **Step 4: Verify build with `npx tsc --noEmit` and commit**

---

### Task 8: Interactive Policy Simulator ("What-If") & Live Health Calculations

**Files:**
- Create: `frontend/src/components/common/Slider.tsx`
- Create: `frontend/src/components/tabs/WhatIfTab.tsx`
- Create: `frontend/src/components/simulator/BeforeAfterComparison.tsx`

**Interfaces:**
- Produces: Real-time slider controls (0-100% cut per source) updating predicted PM2.5, WHO status, and averted deaths/admissions at 60fps

- [ ] **Step 1: Build accessible Slider primitive with value indicators**
- [ ] **Step 2: Build BeforeAfterComparison component showing PM2.5 and health delta**
- [ ] **Step 3: Build WhatIfTab with sliders and instant client-side GEMM evaluation**
- [ ] **Step 4: Verify build with `npx tsc --noEmit` and commit**

---

### Task 9: Timeline Tab with Recharts & Hour Inspection

**Files:**
- Create: `frontend/src/components/tabs/TimelineTab.tsx`
- Create: `frontend/src/components/charts/HourlyTimelineChart.tsx`
- Create: `frontend/src/components/charts/HourlyDetailPanel.tsx`

**Interfaces:**
- Produces: Interactive time series chart with Recharts, crosshairs, hour scrubbing, and click-to-pin breakdown

- [ ] **Step 1: Build HourlyTimelineChart with synchronized tooltip & pinned hour state**
- [ ] **Step 2: Build HourlyDetailPanel displaying the source breakdown at the active hour**
- [ ] **Step 3: Integrate into TimelineTab**
- [ ] **Step 4: Verify build with `npx tsc --noEmit` and commit**

---

### Task 10: Monitoring Stations Tab & Geographic Scatter Map

**Files:**
- Create: `frontend/src/components/tabs/StationsTab.tsx`
- Create: `frontend/src/components/charts/StationScatterMap.tsx`
- Create: `frontend/src/components/charts/StationComparisonList.tsx`

**Interfaces:**
- Produces: Delhi NCR coordinate scatter map with station bubbles colored by dominant source and station comparison list

- [ ] **Step 1: Build StationScatterMap SVG displaying Delhi station coordinates**
- [ ] **Step 2: Build StationComparisonList showing station-by-station source distribution**
- [ ] **Step 3: Integrate into StationsTab**
- [ ] **Step 4: Verify build with `npx tsc --noEmit` and commit**

---

### Task 11: Scientific Evidence & Proof Tab

**Files:**
- Create: `frontend/src/components/tabs/EvidenceTab.tsx`
- Create: `frontend/src/components/charts/CredibleIntervalWhisker.tsx`
- Create: `frontend/src/components/charts/IdentifiabilityHeatmap.tsx`
- Create: `frontend/src/components/evidence/BaselinesTable.tsx`
- Create: `frontend/src/components/evidence/LiteratureComparison.tsx`

**Interfaces:**
- Produces: Whisker plots of 90% credible intervals, correlation heatmap, baseline benchmarking table, and literature ranges

- [ ] **Step 1: Build CredibleIntervalWhisker plot with ground truth markers**
- [ ] **Step 2: Build IdentifiabilityHeatmap cross-correlation grid**
- [ ] **Step 3: Build BaselinesTable and LiteratureComparison components**
- [ ] **Step 4: Integrate into EvidenceTab**
- [ ] **Step 5: Verify build with `npx tsc --noEmit` and commit**

---

### Task 12: CSV Upload & Diagnostic Preview Page

**Files:**
- Create: `frontend/src/components/tabs/UploadTab.tsx`
- Create: `frontend/src/components/upload/Dropzone.tsx`
- Create: `frontend/src/components/upload/ColumnDiagnosticTable.tsx`
- Create: `frontend/src/components/upload/PreviewChart.tsx`

**Interfaces:**
- Produces: Drag-and-drop CSV validator with instant client-side parsing, server verification, and background attribution trigger

- [ ] **Step 1: Build Dropzone with drag-and-drop and file selector**
- [ ] **Step 2: Build ColumnDiagnosticTable showing checkmarks for required and optional columns**
- [ ] **Step 3: Build PreviewChart rendering 48-hour preview**
- [ ] **Step 4: Connect to `/api/upload/validate` and `/api/jobs/run`**
- [ ] **Step 5: Verify build with `npx tsc --noEmit` and commit**

---

### Task 13: Full Integration, End-to-End Verification & Documentation

**Files:**
- Create: `frontend/src/components/jobs/JobStatusBanner.tsx`
- Modify: `README.md`
- Test: Full-stack smoke test

**Interfaces:**
- Produces: Fully functional integrated system with background job banner, verified build, and updated documentation

- [ ] **Step 1: Integrate JobStatusBanner into App layout**
- [ ] **Step 2: Run all backend tests (`pytest`) and frontend tests (`npx tsc --noEmit`, `npm run build`)**
- [ ] **Step 3: Update README.md with instructions on running the FastAPI backend and React frontend**
- [ ] **Step 4: Final commit**
