export type SourceId = 'traffic' | 'industry' | 'dust' | 'biomass' | 'background';

export const SOURCE_COLORS: Record<SourceId, string> = {
  traffic: '#2563eb',    // Blue
  industry: '#8b5cf6',   // Purple
  dust: '#f59e0b',       // Amber
  biomass: '#ef4444',    // Red
  background: '#94a3b8', // Slate
};

export const SOURCE_NAMES: Record<SourceId, string> = {
  traffic: 'Vehicles',
  industry: 'Factories & Power',
  dust: 'Road & Construction Dust',
  biomass: 'Crop-residue Burning',
  background: 'Regional Haze',
};

export const SOURCE_SHORT_NAMES: Record<SourceId, string> = {
  traffic: 'Vehicles',
  industry: 'Factories',
  dust: 'Road dust',
  biomass: 'Crop burning',
  background: 'Regional haze',
};

export const SOURCE_DESCRIPTIONS: Record<SourceId, string> = {
  traffic: 'Exhaust from cars, trucks, buses and two-wheelers. Followed through carbon monoxide (CO) and nitrogen dioxide (NO2) in ambient air.',
  industry: 'Emissions from industrial stacks, boilers and power units. Followed through ambient sulphur dioxide (SO2).',
  dust: 'Suspended coarse mineral particles from traffic shearing, construction sites and unpaved soil. Followed through coarse particle surplus (PM10 - PM2.5).',
  biomass: 'Seasonal agricultural burning in Punjab & Haryana blown into the NCR plume. Followed through NASA VIIRS satellite active fire detections and wind trajectories.',
  background: 'Secondary regional haze and transboundary air already present before reaching local Delhi NCR sources.',
};
