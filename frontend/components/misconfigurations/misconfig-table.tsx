import React, { useState } from 'react';
import MisconfigDetails from './misconfig-details';

interface Misconfiguration {
  service: string;
  resource: string;
  riskLevel: 'Critical' | 'High' | 'Medium' | 'Low';
  description: string;
  compliance: string;
  details: {
    impact: string;
    remediation: string;
    additionalInfo: Record<string, string>;
  };
}

const mockMisconfigurations: Misconfiguration[] = [
  {
    service: 'S3',
    resource: 'data-backup-bucket',
    riskLevel: 'Critical',
    description: 'Public read access enabled',
    compliance: 'CIS 2.1.5',
    details: {
      impact: 'Unauthorized access to sensitive data',
      remediation: '1. Disable public access settings\n2. Update bucket policy\n3. Enable default encryption',
      additionalInfo: {
        'Bucket Policy': 'Allow public read access',
        'Versioning': 'Disabled',
        'Encryption': 'None',
      }
    }
  },
  {
    service: 'IAM',
    resource: 'service-role-prod',
    riskLevel: 'High',
    description: 'Overly permissive IAM role',
    compliance: 'NIST AC-6',
    details: {
      impact: 'Potential privilege escalation',
      remediation: '1. Review role permissions\n2. Apply least privilege principle\n3. Remove unused permissions',
      additionalInfo: {
        'Attached Policies': '10',
        'Last Used': '2025-02-15',
        'Resource Access': 'Full Admin',
      }
    }
  },
  {
    service: 'EC2',
    resource: 'web-server-01',
    riskLevel: 'Medium',
    description: 'Security group allows all inbound traffic',
    compliance: 'PCI DSS 1.3',
    details: {
      impact: 'Increased attack surface',
      remediation: '1. Review security group rules\n2. Remove overly permissive rules\n3. Implement specific IP ranges',
      additionalInfo: {
        'Security Group': 'sg-01234',
        'Open Ports': '0-65535',
        'Source IP': '0.0.0.0/0',
      }
    }
  }
];

const MisconfigTable: React.FC = () => {
  const [selectedMisconfig, setSelectedMisconfig] = useState<Misconfiguration | null>(null);
  const [showDetails, setShowDetails] = useState(false);

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case 'Critical':
        return 'bg-red-100 text-red-800';
      case 'High':
        return 'bg-blue-100 text-blue-800';
      case 'Medium':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <>
      <div className="bg-white shadow-md rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Service</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Resource</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Risk Level</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Compliance</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {mockMisconfigurations.map((misconfig, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{misconfig.service}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{misconfig.resource}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getRiskLevelColor(misconfig.riskLevel)}`}>
                      {misconfig.riskLevel}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">{misconfig.description}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{misconfig.compliance}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      onClick={() => {
                        setSelectedMisconfig(misconfig);
                        setShowDetails(true);
                      }}
                      className="text-blue-600 hover:text-blue-900"
                    >
                      View Details
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Details Modal */}
      {showDetails && selectedMisconfig && (
        <MisconfigDetails
          misconfig={selectedMisconfig}
          onClose={() => setShowDetails(false)}
        />
      )}
    </>
  );
};

export default MisconfigTable;
