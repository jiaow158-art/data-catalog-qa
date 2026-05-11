import { useCallback, useEffect, useMemo } from 'react'
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  type Node,
  type Edge,
  MarkerType,
  Position,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import dagre from 'dagre'
import { useNavigate } from 'react-router-dom'

interface GraphNode {
  id: string
  table_name: string
  display_name: string
  table_type: string
  owner: string
  is_focus: boolean
  depth: number
}

interface GraphEdge {
  id: string
  source: string
  target: string
  label: string
}

interface Props {
  nodes: GraphNode[]
  edges: GraphEdge[]
}

const typeColor: Record<string, string> = {
  fact: '#ff4d4f',
  dim: '#1677ff',
  dwd: '#722ed1',
  dws: '#2f54eb',
  ads: '#52c41a',
}

function layoutDAG(nodes: GraphNode[], edges: GraphEdge[]) {
  const g = new dagre.graphlib.Graph()
  g.setDefaultEdgeLabel(() => ({}))
  g.setGraph({ rankdir: 'LR', nodesep: 60, ranksep: 180, marginx: 40, marginy: 40 })

  for (const n of nodes) {
    g.setNode(n.id, { width: 180, height: 60 })
  }
  for (const e of edges) {
    g.setEdge(e.source, e.target)
  }

  dagre.layout(g)

  return nodes.map((n) => {
    const pos = g.node(n.id)
    return {
      ...n,
      x: pos.x,
      y: pos.y,
    }
  })
}

export default function LineageGraph({ nodes: dataNodes, edges: dataEdges }: Props) {
  const navigate = useNavigate()

  const layoutedNodes = useMemo(() => layoutDAG(dataNodes, dataEdges), [dataNodes, dataEdges])

  const initialNodes: Node[] = useMemo(
    () =>
      layoutedNodes.map((n) => ({
        id: n.id,
        type: 'default',
        position: { x: n.x, y: n.y },
        data: {
          label: (
            <div
              style={{
                padding: '8px 12px',
                borderRadius: 8,
                border: `2px solid ${typeColor[n.table_type] || '#ddd'}`,
                background: n.is_focus ? '#fff7e6' : '#fff',
                cursor: 'pointer',
                minWidth: 160,
                textAlign: 'center',
              }}
            >
              <div style={{ fontWeight: 600, fontSize: 13, color: '#333' }}>
                {n.display_name}
              </div>
              <div style={{ fontSize: 11, color: '#888' }}>{n.table_name}</div>
              {n.owner && (
                <div style={{ fontSize: 10, color: '#aaa', marginTop: 2 }}>
                  {n.owner}
                </div>
              )}
            </div>
          ),
        },
        sourcePosition: Position.Right,
        targetPosition: Position.Left,
      })),
    [layoutedNodes],
  )

  const [xyNodes, setXyNodes, onNodesChange] = useNodesState(initialNodes)

  const initialEdges: Edge[] = useMemo(
    () =>
      dataEdges.map((e) => ({
        id: e.id,
        source: e.source,
        target: e.target,
        label: e.label,
        type: 'smoothstep',
        animated: true,
        style: { stroke: '#b1b1b7', strokeWidth: 1.5 },
        labelStyle: { fontSize: 10, fill: '#666' },
        labelBgStyle: { fill: '#fff', fillOpacity: 0.8 },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          width: 16,
          height: 16,
          color: '#b1b1b7',
        },
      })),
    [dataEdges],
  )

  const [xyEdges, setXyEdges, onEdgesChange] = useEdgesState(initialEdges)

  useEffect(() => {
    setXyNodes(initialNodes)
    setXyEdges(initialEdges)
  }, [initialNodes, initialEdges, setXyNodes, setXyEdges])

  const onNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      navigate(`/tables/${node.id}`)
    },
    [navigate],
  )

  return (
    <div style={{ width: '100%', height: 500, border: '1px solid #f0f0f0', borderRadius: 8 }}>
      <ReactFlow
        nodes={xyNodes}
        edges={xyEdges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        fitView
        fitViewOptions={{ padding: 0.3 }}
        attributionPosition="bottom-right"
      >
        <Background color="#f0f0f0" gap={20} />
        <Controls />
        <MiniMap
          nodeColor={(n) => {
            const dataNode = dataNodes.find((dn) => dn.id === n.id)
            return typeColor[dataNode?.table_type || ''] || '#ddd'
          }}
          maskColor="rgba(0,0,0,0.08)"
        />
      </ReactFlow>
    </div>
  )
}
