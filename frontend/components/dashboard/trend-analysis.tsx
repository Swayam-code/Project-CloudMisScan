"use client"

import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const data = [
  { date: '2024-01', issues: 65 },
  { date: '2024-02', issues: 52 },
  { date: '2024-03', issues: 48 },
  { date: '2024-04', issues: 50 },
  { date: '2024-05', issues: 42 },
]

const CustomXAxis = (props: any) => (
  <XAxis {...props} style={{ fontSize: '12px' }} />
)

const CustomYAxis = (props: any) => (
  <YAxis {...props} style={{ fontSize: '12px' }} />
)

export default function TrendAnalysis() {
  return (
    <Card className="col-span-1">
      <CardHeader>
        <CardTitle>Issue Trends</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <CustomXAxis dataKey="date" />
              <CustomYAxis />
              <Tooltip />
              <Line 
                type="monotone" 
                dataKey="issues" 
                stroke="hsl(var(--primary))" 
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}