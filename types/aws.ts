export interface Misconfiguration {
  type: string;
  severity: 'HIGH' | 'MEDIUM' | 'LOW';
  description: string;
}

export interface Resource {
  id: string;
  resource_id: string;
  type: string;
  name: string;
  relationships: string[];
  misconfigurations: Misconfiguration[];
}

export interface ServiceData {
  [key: string]: Resource[];
}

export interface ComplianceControl {
  id: string;
  title: string;
  status: 'PASS' | 'FAIL' | 'UNKNOWN';
  description: string;
}

export interface ComplianceFramework {
  score: number;
  controls: ComplianceControl[];
}

export interface ComplianceData {
  cis: ComplianceFramework;
  nist: ComplianceFramework;
  pci: ComplianceFramework;
}

export interface TrendData {
  date: string;
  value: number;
}

export interface TrendDataset {
  overall: TrendData[];
  services: {
    [key: string]: TrendData[];
  };
}

export interface RiskMetrics {
  high: number;
  medium: number;
  low: number;
}

export interface DashboardData {
  compliance: ComplianceData;
  trends: TrendDataset;
  services: ServiceData;
  resources: Resource[];
  riskMetrics: RiskMetrics;
}
