import DashboardHeader from '@/components/dashboard/header'
import SecurityOverview from '@/components/dashboard/security-overview'
import TrendAnalysis from '@/components/dashboard/trend-analysis'
import ResourceMap from '@/components/dashboard/resource-map'

export default function Home() {
  return (
    <div className="container mx-auto p-6 space-y-6">
      <DashboardHeader />
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <SecurityOverview />
        <TrendAnalysis />
        <ResourceMap />
      </div>
    </div>
  )
}