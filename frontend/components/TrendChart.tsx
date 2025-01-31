import { TrendData } from '../types/aws';
import { Card, Title, LineChart, Select, SelectItem } from '@tremor/react';
import { format, parseISO } from 'date-fns';
import { useMemo } from 'react';

interface Props {
  data?: TrendData[];
  title: string;
  timeRange: number;
  onTimeRangeChange: (days: number) => void;
}

export default function TrendChart({
  data = [],
  title,
  timeRange,
  onTimeRangeChange,
}: Props) {
  const formattedData = useMemo(() => {
    if (!data || !Array.isArray(data)) {
      console.warn('TrendChart: Invalid or missing data', { data });
      return [];
    }
    
    return data.map((item) => {
      if (!item.date || typeof item.value !== 'number') {
        console.warn('TrendChart: Invalid data point', { item });
        return null;
      }
      return {
        date: format(parseISO(item.date), 'MMM d, yyyy'),
        value: item.value,
      };
    }).filter(Boolean);
  }, [data]);

  console.log('TrendChart:', { title, timeRange, data, formattedData });

  if (!data || data.length === 0) {
    return (
      <Card className="h-96">
        <div className="flex justify-between items-center mb-4">
          <Title>{title}</Title>
          <Select
            value={timeRange.toString()}
            onValueChange={(value) => onTimeRangeChange(Number(value))}
            className="w-40"
          >
            <SelectItem value="7">Last 7 days</SelectItem>
            <SelectItem value="30">Last 30 days</SelectItem>
            <SelectItem value="90">Last 90 days</SelectItem>
          </Select>
        </div>
        <div className="h-64 flex items-center justify-center text-gray-500">
          No trend data available
        </div>
      </Card>
    );
  }

  return (
    <Card className="h-96">
      <div className="flex justify-between items-center mb-4">
        <Title>{title}</Title>
        <Select
          value={timeRange.toString()}
          onValueChange={(value) => onTimeRangeChange(Number(value))}
          className="w-40"
        >
          <SelectItem value="7">Last 7 days</SelectItem>
          <SelectItem value="30">Last 30 days</SelectItem>
          <SelectItem value="90">Last 90 days</SelectItem>
        </Select>
      </div>
      <LineChart
        data={formattedData}
        index="date"
        categories={['value']}
        colors={['blue']}
        valueFormatter={(value) => value.toFixed(2)}
        showLegend={false}
        className="h-64 mt-4"
      />
    </Card>
  );
}
