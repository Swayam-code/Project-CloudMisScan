import React from 'react';

interface MisconfigDetailsProps {
  misconfig: {
    service: string;
    resource: string;
    riskLevel: string;
    description: string;
    compliance: string;
    details: {
      impact: string;
      remediation: string;
      additionalInfo: Record<string, string>;
    };
  };
  onClose: () => void;
}

const MisconfigDetails: React.FC<MisconfigDetailsProps> = ({ misconfig, onClose }) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-start mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Configuration Details</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-500"
            >
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div className="space-y-6">
            {/* Basic Info */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-500">Service</label>
                <p className="mt-1 text-sm text-gray-900">{misconfig.service}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-500">Resource</label>
                <p className="mt-1 text-sm text-gray-900">{misconfig.resource}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-500">Risk Level</label>
                <p className="mt-1 text-sm text-gray-900">{misconfig.riskLevel}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-500">Compliance</label>
                <p className="mt-1 text-sm text-gray-900">{misconfig.compliance}</p>
              </div>
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-gray-500">Description</label>
              <p className="mt-1 text-sm text-gray-900">{misconfig.description}</p>
            </div>

            {/* Impact */}
            <div>
              <label className="block text-sm font-medium text-gray-500">Impact</label>
              <p className="mt-1 text-sm text-gray-900">{misconfig.details.impact}</p>
            </div>

            {/* Remediation Steps */}
            <div>
              <label className="block text-sm font-medium text-gray-500">Remediation Steps</label>
              <div className="mt-1 text-sm text-gray-900 whitespace-pre-line">
                {misconfig.details.remediation}
              </div>
            </div>

            {/* Additional Info */}
            <div>
              <label className="block text-sm font-medium text-gray-500 mb-2">Additional Information</label>
              <div className="bg-gray-50 rounded-lg p-4">
                <dl className="grid grid-cols-2 gap-4">
                  {Object.entries(misconfig.details.additionalInfo).map(([key, value]) => (
                    <div key={key}>
                      <dt className="text-sm font-medium text-gray-500">{key}</dt>
                      <dd className="mt-1 text-sm text-gray-900">{value}</dd>
                    </div>
                  ))}
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 rounded-b-lg">
          <button
            onClick={onClose}
            className="w-full inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default MisconfigDetails;
