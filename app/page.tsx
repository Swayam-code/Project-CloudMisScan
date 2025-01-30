'use client';

import { useState, useEffect } from 'react';
import ComplianceOverview from '@/components/ComplianceOverview';
import TrendChart from '@/components/TrendChart';
import ServiceMisconfigurations from '@/components/ServiceMisconfigurations';
import RiskAssessment from '@/components/RiskAssessment';
import ResourceRelationships from '@/components/ResourceRelationships';
import ReportGenerator from '@/components/ReportGenerator';
import { DashboardData } from '@/types/aws';
import { Tab } from '@headlessui/react';

export default function Home() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState(30);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        console.log('Fetching dashboard data...');
        
        const response = await fetch(`/api/dashboard?days=${timeRange}`);
        console.log('Response status:', response.status);
        
        if (!response.ok) {
          const errorText = await response.text();
          console.error('Response error:', errorText);
          throw new Error(`Failed to fetch dashboard data: ${errorText}`);
        }
        
        const jsonData = await response.json();
        console.log('Dashboard data:', jsonData);
        
        if (!jsonData || typeof jsonData !== 'object') {
          throw new Error('Invalid dashboard data received');
        }
        
        setData(jsonData);
      } catch (err) {
        console.error('Error fetching data:', err);
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [timeRange]);

  const handleGenerateReport = async (format: string, type: string) => {
    try {
      const response = await fetch(`/api/reports/generate?format=${format}&type=${type}`);
      if (!response.ok) throw new Error('Failed to generate report');
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `security-report-${type}-${new Date().toISOString()}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error generating report:', error);
    }
  };

  if (loading) {
    return (
      <main className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading dashboard data...</p>
          </div>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="container mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8">
          <h2 className="text-red-700 font-semibold mb-2">Error</h2>
          <p className="text-red-600">{error}</p>
        </div>
      </main>
    );
  }

  return (
    <main className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">AWS Security Dashboard</h1>
        <ReportGenerator onGenerate={handleGenerateReport} />
      </div>
      
      <Tab.Group>
        <Tab.List className="flex space-x-1 rounded-xl bg-blue-900/20 p-1 mb-8">
          <Tab className={({ selected }) =>
            `w-full rounded-lg py-2.5 text-sm font-medium leading-5
             ${selected
              ? 'bg-white text-blue-700 shadow'
              : 'text-blue-100 hover:bg-white/[0.12] hover:text-white'
            }`
          }>
            Overview
          </Tab>
          <Tab className={({ selected }) =>
            `w-full rounded-lg py-2.5 text-sm font-medium leading-5
             ${selected
              ? 'bg-white text-blue-700 shadow'
              : 'text-blue-100 hover:bg-white/[0.12] hover:text-white'
            }`
          }>
            Resources
          </Tab>
          <Tab className={({ selected }) =>
            `w-full rounded-lg py-2.5 text-sm font-medium leading-5
             ${selected
              ? 'bg-white text-blue-700 shadow'
              : 'text-blue-100 hover:bg-white/[0.12] hover:text-white'
            }`
          }>
            Analytics
          </Tab>
        </Tab.List>

        <Tab.Panels>
          <Tab.Panel>
            <div className="grid gap-8">
              {data && (
                <>
                  <div className="grid md:grid-cols-2 gap-8">
                    <ComplianceOverview data={data.compliance} />
                    <RiskAssessment metrics={data.riskMetrics} />
                  </div>
                  
                  <ServiceMisconfigurations services={data.services} />
                </>
              )}
            </div>
          </Tab.Panel>

          <Tab.Panel>
            <div className="grid gap-8">
              {data && (
                <>
                  <ResourceRelationships resources={data.resources} />
                </>
              )}
            </div>
          </Tab.Panel>

          <Tab.Panel>
            <div className="grid gap-8">
              {data && (
                <>
                  <div className="grid md:grid-cols-2 gap-8">
                    <TrendChart
                      data={data.trends?.overall}
                      title="Overall Security Trend"
                      timeRange={timeRange}
                      onTimeRangeChange={setTimeRange}
                    />
                    <TrendChart
                      data={data.trends?.services?.ec2}
                      title="EC2 Security Trend"
                      timeRange={timeRange}
                      onTimeRangeChange={setTimeRange}
                    />
                  </div>
                </>
              )}
            </div>
          </Tab.Panel>
        </Tab.Panels>
      </Tab.Group>
    </main>
  );
}
