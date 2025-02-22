"use client"

import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts'

const data = [
  { name: 'Critical', value: 3, color: '#ef4444' },
  { name: 'High', value: 8, color: '#f97316' },
  { name: 'Medium', value: 15, color: '#eab308' },
  { name: 'Low', value: 24, color: '#22c55e' },
]

const RADIAN = Math.PI / 180
const renderCustomizedLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent, index, name, value }: any) => {
  const radius = innerRadius + (outerRadius - innerRadius) * 0.5
  const x = cx + radius * Math.cos(-midAngle * RADIAN)
  const y = cy + radius * Math.sin(-midAngle * RADIAN)
  const cos = Math.cos(-midAngle * RADIAN)
  const textAnchor = cos >= 0 ? 'start' : 'end'
  const percentageValue = (percent * 100).toFixed(0)

  // Skip label if percentage is too small
  if (Number(percentageValue) < 5) return null

  // Adjust x position to prevent overflow
  const adjustedX = cos >= 0 ? Math.min(x, cx + 70) : Math.max(x, cx - 70)

  return (
    <g>
      <text
        x={adjustedX}
        y={y}
        textAnchor={textAnchor}
        className="text-[10px] font-medium fill-[#64748b]"
        dominantBaseline="central"
      >
        {`${value} ${name} (${percentageValue}%)`}
      </text>
    </g>
  )
}

export default function SecurityOverview() {
  const total = data.reduce((sum, item) => sum + item.value, 0)
  
  return (
    <Card className="col-span-1">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle>Risk Overview</CardTitle>
        <span className="text-sm text-muted-foreground">{total} issues</span>
      </CardHeader>
      <CardContent>
        <div className="h-[200px] relative">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart margin={{ top: 10, right: 10, bottom: 10, left: 10 }}>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={renderCustomizedLabel}
                innerRadius={35}
                outerRadius={60}
                fill="#8884d8"
                dataKey="value"
                paddingAngle={2}
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="mt-4 space-y-2">
          {data.map((item, index) => (
            <div key={index} className="flex items-center justify-between p-2 bg-accent rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: item.color }} />
                <span>{item.name}</span>
              </div>
              <span className="text-sm font-medium">{item.value} issues</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}