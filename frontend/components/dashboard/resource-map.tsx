"use client"

import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

export default function ResourceMap() {
  return (
    <Card className="col-span-1">
      <CardHeader>
        <CardTitle>Resource Map</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-3 bg-accent rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-red-500 rounded-full" />
              <span>EC2 Instances</span>
            </div>
            <Badge>12 Resources</Badge>
          </div>
          
          <div className="flex items-center justify-between p-3 bg-accent rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-blue-500 rounded-full" />
              <span>S3 Buckets</span>
            </div>
            <Badge>8 Resources</Badge>
          </div>
          
          <div className="flex items-center justify-between p-3 bg-accent rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-green-500 rounded-full" />
              <span>RDS Databases</span>
            </div>
            <Badge>5 Resources</Badge>
          </div>
          
          <div className="flex items-center justify-between p-3 bg-accent rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-yellow-500 rounded-full" />
              <span>Security Groups</span>
            </div>
            <Badge>15 Resources</Badge>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}