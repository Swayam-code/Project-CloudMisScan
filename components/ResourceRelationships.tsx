import { Card, Title } from '@tremor/react';
import dynamic from 'next/dynamic';

const Graph = dynamic(() => import('react-force-graph-2d'), { ssr: false });

interface Resource {
  id: string;
  type: string;
  name: string;
  relationships: string[];
}

interface Props {
  resources: Resource[];
}

export default function ResourceRelationships({ resources }: Props) {
  const graphData = {
    nodes: resources.map(resource => ({
      id: resource.id,
      name: resource.name,
      val: 1,
      color: getResourceColor(resource.type),
    })),
    links: resources.flatMap(resource =>
      resource.relationships.map(targetId => ({
        source: resource.id,
        target: targetId,
      }))
    ),
  };

  function getResourceColor(type: string) {
    switch (type.toLowerCase()) {
      case 'ec2':
        return '#ff9900';
      case 's3':
        return '#e31a1c';
      case 'rds':
        return '#33a02c';
      case 'iam':
        return '#1f78b4';
      default:
        return '#6a3d9a';
    }
  }

  return (
    <Card className="mx-auto">
      <Title>Resource Relationships</Title>
      <div className="h-[500px] w-full mt-4">
        <Graph
          graphData={graphData}
          nodeLabel="name"
          nodeRelSize={6}
          nodeAutoColorBy="type"
          linkDirectionalParticles={2}
        />
      </div>
    </Card>
  );
}

function getResourceTypeIcon(type: string) {
  switch (type.toLowerCase()) {
    case 'ec2':
      return '🖥️';
    case 's3':
      return '💾';
    case 'rds':
      return '🗄️';
    case 'iam':
      return '🔑';
    default:
      return '📦';
  }
}
