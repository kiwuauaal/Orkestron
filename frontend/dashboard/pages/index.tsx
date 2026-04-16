import type { NextPage } from 'next';
import Head from 'next/head';
import { useState, useEffect, useCallback } from 'react';

interface Agent {
  name: string;
  status: string;
  updated_at: string;
}

interface Task {
  task_id: string;
  title: string;
  description: string;
  status: string;
  type: string;
}

interface Log {
  timestamp: string;
  level: string;
  message: string;
}

export default function Dashboard() {
  const [agents, setAgents] = useState<Array<{name: string; status: string; updated_at: string}>>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [logs, setLogs] = useState<Log[]>([]);
  const [cycleStatus, setCycleStatus] = useState<string>('idle');
  const [deploymentStatus, setDeploymentStatus] = useState<string>('unknown');
  const [wsConnected, setWsConnected] = useState<boolean>(false);

  // Fetch data from API
  const fetchData = useCallback(async () => {
    try {
      const [agentsRes, tasksRes, logsRes, cycleRes, deploymentRes] = await Promise.all([
        fetch('http://localhost:8000/agents/status'),
        fetch('http://localhost:8000/tasks/pending'),
        fetch('http://localhost:8000/logs?limit=50'),
        fetch('http://localhost:8000/cycle/status'),
        fetch('http://localhost:8000/deployment/status')
      ]);

      if (!agentsRes.ok || !tasksRes.ok || !logsRes.ok || !cycleRes.ok || !deploymentRes.ok) {
        console.warn('Some API requests failed');
        return;
      }

      const agentsData = await agentsRes.json();
      const tasksData = await tasksRes.json();
      const logsData = await logsRes.json();
      const cycleData = await cycleRes.json();
      const deploymentData = await deploymentRes.json();

      if (agentsData && typeof agentsData === 'object') {
        setAgents(Object.entries(agentsData).map(([name, data]: [string, any]) => ({
          name,
          ...(typeof data === 'object' ? data : { status: 'unknown', updated_at: '' })
        })));
      }
      setTasks(Array.isArray(tasksData.tasks) ? tasksData.tasks : []);
      setLogs(Array.isArray(logsData) ? logsData : []);
      setCycleStatus(cycleData?.phase || 'idle');
      setDeploymentStatus(deploymentData?.status || 'unknown');
    } catch (error) {
      console.error('Failed to fetch data:', error);
    }
  }, []);

  // WebSocket connection
  useEffect(() => {
    let ws: WebSocket | null = null;
    
    try {
      ws = new WebSocket('ws://localhost:8000/ws');

      ws.onopen = () => {
        setWsConnected(true);
        console.log('WebSocket connected');
      };

      ws.onmessage = (event: MessageEvent) => {
        try {
          const data = JSON.parse(event.data);
          // Update state based on WebSocket message
          fetchData();
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      ws.onclose = () => {
        setWsConnected(false);
        console.log('WebSocket disconnected');
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setWsConnected(false);
      };
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      setWsConnected(false);
    }

    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [fetchData]);

  // Poll for updates
  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <>
      <Head>
        <title>Orkestron Dashboard</title>
        <meta name="description" content="Orkestron - Multi-agent orchestration system dashboard" />
      </Head>

      <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
        <header style={{ marginBottom: '30px' }}>
          <h1>Orkestron Dashboard</h1>
          <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
            <span style={{ 
              padding: '5px 10px', 
              borderRadius: '5px',
              backgroundColor: wsConnected ? '#4CAF50' : '#f44336',
              color: 'white'
            }}>
              {wsConnected ? '● Connected' : '● Disconnected'}
            </span>
            <span>Cycle: <strong>{cycleStatus}</strong></span>
            <span>Deployment: <strong>{deploymentStatus}</strong></span>
          </div>
        </header>

        {/* Agent Status Panel */}
        <section style={{ marginBottom: '30px' }}>
          <h2>Agent Status</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '15px' }}>
            {agents.map((agent) => (
              <div 
                key={agent.name}
                style={{
                  padding: '15px',
                  borderRadius: '8px',
                  backgroundColor: '#f5f5f5',
                  borderLeft: `4px solid ${getStatusColor(agent.status)}`
                }}
              >
                <h3 style={{ margin: '0 0 10px 0' }}>{agent.name}</h3>
                <p style={{ margin: '5px 0' }}>
                  Status: <strong>{agent.status}</strong>
                </p>
                <p style={{ margin: '5px 0', fontSize: '12px', color: '#666' }}>
                  Updated: {agent.updated_at ? new Date(agent.updated_at).toLocaleTimeString() : 'N/A'}
                </p>
              </div>
            ))}
          </div>
        </section>

        {/* Task Board */}
        <section style={{ marginBottom: '30px' }}>
          <h2>Task Board</h2>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ backgroundColor: '#f5f5f5' }}>
                  <th style={thStyle}>Task ID</th>
                  <th style={thStyle}>Title</th>
                  <th style={thStyle}>Type</th>
                  <th style={thStyle}>Status</th>
                </tr>
              </thead>
              <tbody>
                {tasks.map((task) => (
                  <tr key={task.task_id}>
                    <td style={tdStyle}>{task.task_id}</td>
                    <td style={tdStyle}>{task.title}</td>
                    <td style={tdStyle}>{task.type}</td>
                    <td style={tdStyle}>
                      <span style={{
                        padding: '3px 8px',
                        borderRadius: '3px',
                        backgroundColor: getStatusColor(task.status),
                        color: 'white',
                        fontSize: '12px'
                      }}>
                        {task.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {tasks.length === 0 && (
              <p style={{ textAlign: 'center', color: '#999', padding: '20px' }}>
                No pending tasks
              </p>
            )}
          </div>
        </section>

        {/* Logs Viewer */}
        <section style={{ marginBottom: '30px' }}>
          <h2>Recent Logs</h2>
          <div style={{
            maxHeight: '400px',
            overflowY: 'auto',
            backgroundColor: '#1e1e1e',
            color: '#d4d4d4',
            padding: '15px',
            borderRadius: '8px',
            fontFamily: 'monospace',
            fontSize: '13px'
          }}>
            {logs.map((log, index) => (
              <div key={index} style={{ marginBottom: '5px' }}>
                <span style={{ color: '#888' }}>
                  [{log.timestamp ? new Date(log.timestamp).toLocaleTimeString() : 'N/A'}]
                </span>
                <span style={{ 
                  color: log.level === 'error' ? '#f44336' : 
                         log.level === 'warning' ? '#ff9800' : '#4CAF50'
                }}>
                  [{log.level?.toUpperCase() || 'INFO'}]
                </span>
                <span>{log.message || ''}</span>
              </div>
            ))}
            {logs.length === 0 && (
              <p style={{ color: '#666' }}>No logs available</p>
            )}
          </div>
        </section>

        {/* Manual Override */}
        <section style={{ marginBottom: '30px' }}>
          <h2>Manual Override</h2>
          <div style={{ display: 'flex', gap: '10px' }}>
            <button 
              style={buttonStyle}
              onClick={async () => {
                try {
                  await fetch('http://localhost:8000/cycle/start', { method: 'POST' });
                  fetchData();
                } catch (error) {
                  console.error('Failed to start cycle:', error);
                }
              }}
            >
              Start Cycle
            </button>
            <button 
              style={buttonStyle}
              onClick={async () => {
                try {
                  await fetch('http://localhost:8000/orchestrate', { method: 'POST' });
                  fetchData();
                } catch (error) {
                  console.error('Failed to orchestrate tasks:', error);
                }
              }}
            >
              Orchestrate Tasks
            </button>
            <button 
              style={{...buttonStyle, backgroundColor: '#f44336'}}
              onClick={() => {
                console.log('Emergency stop triggered');
                // TODO: Implement emergency stop logic
              }}
            >
              Emergency Stop
            </button>
          </div>
        </section>
      </div>
    </>
  );
}

interface CSSProperties {
  padding?: string;
  textAlign?: 'left' | 'right' | 'center';
  borderBottom?: string;
  backgroundColor?: string;
  color?: string;
  border?: string;
  borderRadius?: string;
  cursor?: string;
  fontSize?: string;
}

const thStyle: CSSProperties = {
  padding: '12px',
  textAlign: 'left',
  borderBottom: '2px solid #ddd'
};

const tdStyle: CSSProperties = {
  padding: '12px',
  borderBottom: '1px solid #ddd'
};

const buttonStyle: CSSProperties = {
  padding: '10px 20px',
  backgroundColor: '#2196F3',
  color: 'white',
  border: 'none',
  borderRadius: '5px',
  cursor: 'pointer',
  fontSize: '14px'
};

function getStatusColor(status: string): string {
  switch (status?.toLowerCase()) {
    case 'working':
    case 'running':
    case 'active':
      return '#2196F3';
    case 'completed':
    case 'success':
      return '#4CAF50';
    case 'failed':
    case 'error':
      return '#f44336';
    case 'pending':
      return '#ff9800';
    case 'idle':
      return '#9e9e9e';
    default:
      return '#9e9e9e';
  }
}
