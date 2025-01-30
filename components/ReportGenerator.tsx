import { Card, Title, Button, Select, SelectItem } from '@tremor/react';
import { useState } from 'react';
import { DocumentArrowDownIcon } from '@heroicons/react/24/outline';

interface Props {
  onGenerate: (format: string, type: string) => Promise<void>;
}

export default function ReportGenerator({ onGenerate }: Props) {
  const [format, setFormat] = useState('pdf');
  const [type, setType] = useState('full');
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    try {
      setLoading(true);
      await onGenerate(format, type);
    } catch (error) {
      console.error('Error generating report:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="mx-auto">
      <Title>Generate Report</Title>
      <div className="mt-6 space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Report Type
          </label>
          <Select value={type} onValueChange={setType}>
            <SelectItem value="full">Full Assessment</SelectItem>
            <SelectItem value="compliance">Compliance Status</SelectItem>
            <SelectItem value="trends">Historical Trends</SelectItem>
            <SelectItem value="resources">Resource Analysis</SelectItem>
          </Select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Format
          </label>
          <Select value={format} onValueChange={setFormat}>
            <SelectItem value="pdf">PDF</SelectItem>
            <SelectItem value="csv">CSV</SelectItem>
            <SelectItem value="json">JSON</SelectItem>
          </Select>
        </div>

        <Button
          icon={DocumentArrowDownIcon}
          onClick={handleGenerate}
          loading={loading}
          loadingText="Generating..."
          size="lg"
          color="blue"
          className="w-full"
        >
          Generate Report
        </Button>
      </div>
    </Card>
  );
}
