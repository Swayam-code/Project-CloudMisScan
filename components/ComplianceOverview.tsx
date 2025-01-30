import { ComplianceData } from '../types/aws';

interface ComplianceOverviewProps {
  data: ComplianceData;
}

export default function ComplianceOverview({ data }: ComplianceOverviewProps) {
  if (!data || 'error' in data) {
    return (
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">Compliance Overview</h2>
        <p className="text-red-500">
          {data?.error || 'Failed to load compliance data'}
        </p>
      </div>
    );
  }

  const frameworks = [
    { key: 'cis', name: 'CIS Benchmark' },
    { key: 'nist', name: 'NIST Framework' },
    { key: 'pci', name: 'PCI DSS' },
  ];

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h2 className="text-xl font-semibold mb-4">Compliance Overview</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {frameworks.map(({ key, name }) => {
          const framework = data[key as keyof ComplianceData];
          return (
            <div key={key} className="p-4 border rounded-lg">
              <h3 className="font-medium text-lg mb-2">{name}</h3>
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-600">Compliance Score:</span>
                <span className="font-semibold">{framework?.score || 0}%</span>
              </div>
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-blue-500 rounded-full"
                  style={{ width: `${framework?.score || 0}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
