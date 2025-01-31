import { Card, Title, DonutChart, Legend } from '@tremor/react';

interface RiskMetrics {
  high: number;
  medium: number;
  low: number;
}

interface Props {
  metrics: RiskMetrics;
}

export default function RiskAssessment({ metrics }: Props) {
  const data = [
    { name: 'High Risk', value: metrics.high, color: 'rose' },
    { name: 'Medium Risk', value: metrics.medium, color: 'amber' },
    { name: 'Low Risk', value: metrics.low, color: 'emerald' },
  ];

  return (
    <Card className="mx-auto">
      <Title>Risk Assessment</Title>
      <div className="mt-6">
        <DonutChart
          data={data}
          category="value"
          index="name"
          valueFormatter={(number) => number.toString()}
          colors={['rose', 'amber', 'emerald']}
          className="mt-6"
        />
      </div>
      <Legend
        className="mt-6"
        categories={['High Risk', 'Medium Risk', 'Low Risk']}
        colors={['rose', 'amber', 'emerald']}
      />
    </Card>
  );
}
