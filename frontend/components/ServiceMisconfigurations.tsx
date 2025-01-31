import { ServiceData } from '@/types/aws';
import { Card, Title, Badge } from '@tremor/react';
import { ExclamationTriangleIcon, InformationCircleIcon, CheckCircleIcon } from '@heroicons/react/24/solid';
import { useMemo } from 'react';

interface Props {
  services?: ServiceData;
}

export default function ServiceMisconfigurations({ services = {} }: Props) {
  if (!services || Object.keys(services).length === 0) {
    return (
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">Service Misconfigurations</h2>
        <p className="text-gray-500">No misconfigurations found</p>
      </div>
    );
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'HIGH':
        return 'rose';
      case 'MEDIUM':
        return 'amber';
      case 'LOW':
        return 'emerald';
      default:
        return 'slate';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'HIGH':
        return ExclamationTriangleIcon;
      case 'MEDIUM':
        return InformationCircleIcon;
      case 'LOW':
        return CheckCircleIcon;
      default:
        return InformationCircleIcon;
    }
  };

  const resourcesList = useMemo(() => {
    return Object.entries(services).map(([service, resources]) => ({
      service,
      resources: resources.map((resource) => ({
        ...resource,
        misconfigurations: resource.misconfigurations.map((issue) => ({
          ...issue,
          severityColor: getSeverityColor(issue.severity),
          Icon: getSeverityIcon(issue.severity)
        }))
      }))
    }));
  }, [services]);

  return (
    <Card>
      <Title>Service Misconfigurations</Title>
      <div className="mt-4 space-y-4">
        {resourcesList.map((service) => (
          <div key={service.service} className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <h3 className="font-medium text-gray-900 dark:text-gray-100 capitalize">{service.service}</h3>
            {service.resources.length === 0 ? (
              <p className="text-gray-500">No issues found</p>
            ) : (
              <div className="space-y-4">
                {service.resources.map((resource) => (
                  <div key={resource.resource_id} className="bg-gray-50 p-4 rounded">
                    <p className="font-medium mb-2">Resource ID: {resource.resource_id}</p>
                    <div className="space-y-2">
                      {resource.misconfigurations.map((issue, index) => (
                        <div
                          key={index}
                          className="flex items-start space-x-2 text-sm"
                        >
                          <issue.Icon
                            className={`h-5 w-5 text-${issue.severityColor}-500 shrink-0`}
                            aria-hidden="true"
                          />
                          <div>
                            <Badge color={issue.severityColor}>
                              {issue.type}
                            </Badge>
                            <p className="mt-1 text-gray-600 dark:text-gray-300">
                              {issue.description}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </Card>
  );
}
