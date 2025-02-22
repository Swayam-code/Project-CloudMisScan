"use client"

import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Shield, AlertTriangle, CheckCircle } from "lucide-react"

export default function DashboardHeader() {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Security Dashboard</h1>
        <Badge variant="destructive" className="text-sm">
          3 Critical Issues
        </Badge>
      </div>
      
      <div className="grid gap-4 md:grid-cols-3">
        <Card className="p-4">
          <div className="flex items-center space-x-4">
            <Shield className="h-8 w-8 text-green-500" />
            <div>
              <p className="text-sm text-muted-foreground">Overall Score</p>
              <p className="text-2xl font-bold">85%</p>
            </div>
          </div>
        </Card>
        
        <Card className="p-4">
          <div className="flex items-center space-x-4">
            <AlertTriangle className="h-8 w-8 text-yellow-500" />
            <div>
              <p className="text-sm text-muted-foreground">Active Alerts</p>
              <p className="text-2xl font-bold">12</p>
            </div>
          </div>
        </Card>
        
        <Card className="p-4">
          <div className="flex items-center space-x-4">
            <CheckCircle className="h-8 w-8 text-blue-500" />
            <div>
              <p className="text-sm text-muted-foreground">Compliant Resources</p>
              <p className="text-2xl font-bold">94%</p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}