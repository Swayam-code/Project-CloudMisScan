"use client"

import { useState } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { Shield, AlertTriangle, Info } from "lucide-react"

const misconfigurations = [
  {
    id: 1,
    service: "S3",
    resource: "data-backup-bucket",
    riskLevel: "Critical",
    description: "Public read access enabled",
    compliance: "CIS 2.1.5",
    remediation: "Disable public access and implement bucket policy",
  },
  {
    id: 2,
    service: "IAM",
    resource: "service-role-prod",
    riskLevel: "High",
    description: "Overly permissive IAM role",
    compliance: "NIST AC-6",
    remediation: "Apply principle of least privilege",
  },
  {
    id: 3,
    service: "EC2",
    resource: "web-server-01",
    riskLevel: "Medium",
    description: "Security group allows all inbound traffic",
    compliance: "PCI DSS 1.3",
    remediation: "Restrict inbound traffic to necessary ports",
  },
]

const getRiskBadgeVariant = (risk: string) => {
  switch (risk.toLowerCase()) {
    case "critical":
      return "destructive"
    case "high":
      return "default"
    case "medium":
      return "secondary"
    default:
      return "outline"
  }
}

export default function Misconfigurations() {
  const [selectedItem, setSelectedItem] = useState<number | null>(null)

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Security Misconfigurations</h1>
        <Button variant="outline">Export Report</Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Critical Issues</CardTitle>
            <Shield className="h-4 w-4 text-destructive" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">1</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">High Risk</CardTitle>
            <AlertTriangle className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">1</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Medium Risk</CardTitle>
            <Info className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">1</div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Service</TableHead>
                <TableHead>Resource</TableHead>
                <TableHead>Risk Level</TableHead>
                <TableHead>Description</TableHead>
                <TableHead>Compliance</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {misconfigurations.map((item) => (
                <TableRow key={item.id} className="cursor-pointer hover:bg-accent">
                  <TableCell className="font-medium">{item.service}</TableCell>
                  <TableCell>{item.resource}</TableCell>
                  <TableCell>
                    <Badge variant={getRiskBadgeVariant(item.riskLevel)}>
                      {item.riskLevel}
                    </Badge>
                  </TableCell>
                  <TableCell>{item.description}</TableCell>
                  <TableCell>{item.compliance}</TableCell>
                  <TableCell>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setSelectedItem(item.id)}
                    >
                      View Details
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}