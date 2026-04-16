<template>
  <div class="monitor">
    <header>
      <h1>Orkestron Real-Time Monitor</h1>
      <div class="connection-status" :class="{ connected: isConnected }">
        {{ isConnected ? '● Connected' : '● Disconnected' }}
      </div>
    </header>

    <div class="dashboard-grid">
      <!-- Live Metrics -->
      <div class="card">
        <h2>Live Metrics</h2>
        <div class="metrics">
          <div class="metric">
            <span class="label">Cycle Phase</span>
            <span class="value">{{ cycleStatus.phase || 'idle' }}</span>
          </div>
          <div class="metric">
            <span class="label">Pending Tasks</span>
            <span class="value">{{ pendingTasksCount }}</span>
          </div>
          <div class="metric">
            <span class="label">Active Agents</span>
            <span class="value">{{ activeAgentsCount }}</span>
          </div>
        </div>
      </div>

      <!-- Cycle Progress -->
      <div class="card">
        <h2>Cycle Progress</h2>
        <div class="cycle-steps">
          <div 
            v-for="step in cycleSteps" 
            :key="step"
            class="cycle-step"
            :class="{ active: cycleStatus.phase === step }"
          >
            {{ step }}
          </div>
        </div>
      </div>

      <!-- Agent Health -->
      <div class="card">
        <h2>Agent Health</h2>
        <div class="agents-grid">
          <div 
            v-for="(agent, name) in agents" 
            :key="name"
            class="agent-card"
            :class="agent.status"
          >
            <div class="agent-name">{{ name }}</div>
            <div class="agent-status">{{ agent.status }}</div>
            <div class="agent-updated">{{ formatTime(agent.updated_at) }}</div>
          </div>
        </div>
      </div>

      <!-- Real-time Logs -->
      <div class="card logs-card">
        <h2>Real-Time Logs</h2>
        <div class="logs-container">
          <div v-for="(log, index) in logs" :key="index" class="log-entry">
            <span class="log-time">{{ formatTime(log.timestamp) }}</span>
            <span :class="['log-level', log.level]">{{ log.level }}</span>
            <span class="log-message">{{ log.message }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

const isConnected = ref(false);
const cycleStatus = ref({});
const agents = ref({});
const logs = ref([]);
const pendingTasksCount = ref(0);
const activeAgentsCount = ref(0);

const cycleSteps = ['trigger', 'check', 'brain', 'build', 'guard', 'sleep'];

let ws = null;
let pollingInterval = null;

// WebSocket connection
const connectWebSocket = () => {
  ws = new WebSocket('ws://localhost:8000/ws');
  
  ws.onopen = () => {
    isConnected.value = true;
    console.log('WebSocket connected');
  };
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    fetchData();
  };
  
  ws.onclose = () => {
    isConnected.value = false;
    console.log('WebSocket disconnected');
    // Reconnect after 3 seconds
    setTimeout(connectWebSocket, 3000);
  };
};

// Fetch data from API
const fetchData = async () => {
  try {
    const [cycleRes, agentsRes, tasksRes, logsRes] = await Promise.all([
      fetch('http://localhost:8000/cycle/status'),
      fetch('http://localhost:8000/agents/status'),
      fetch('http://localhost:8000/tasks/pending'),
      fetch('http://localhost:8000/logs?limit=100')
    ]);

    cycleStatus.value = await cycleRes.json();
    agents.value = await agentsRes.json();
    const tasksData = await tasksRes.json();
    logs.value = await logsRes.json();

    pendingTasksCount.value = tasksData.count || 0;
    activeAgentsCount.value = Object.values(agents.value).filter(
      agent => agent.status === 'working'
    ).length;
  } catch (error) {
    console.error('Failed to fetch data:', error);
  }
};

// Format time
const formatTime = (timestamp) => {
  if (!timestamp) return 'N/A';
  return new Date(timestamp).toLocaleTimeString();
};

onMounted(() => {
  connectWebSocket();
  fetchData();
  
  // Poll for updates every 3 seconds
  pollingInterval = setInterval(fetchData, 3000);
});

onUnmounted(() => {
  if (ws) ws.close();
  if (pollingInterval) clearInterval(pollingInterval);
});
</script>

<style scoped>
.monitor {
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: #f0f2f5;
  min-height: 100vh;
}

header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.connection-status {
  padding: 8px 16px;
  border-radius: 20px;
  background: #f44336;
  color: white;
  font-weight: bold;
}

.connection-status.connected {
  background: #4CAF50;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.card h2 {
  margin: 0 0 20px 0;
  font-size: 1.5rem;
  color: #333;
}

.metrics {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.metric {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  background: #f5f5f5;
  border-radius: 8px;
}

.metric .label {
  color: #666;
}

.metric .value {
  font-weight: bold;
  color: #2196F3;
}

.cycle-steps {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.cycle-step {
  padding: 12px;
  background: #e0e0e0;
  border-radius: 8px;
  text-align: center;
  transition: all 0.3s;
}

.cycle-step.active {
  background: #2196F3;
  color: white;
  font-weight: bold;
}

.agents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 15px;
}

.agent-card {
  padding: 15px;
  border-radius: 8px;
  background: #f5f5f5;
  border-left: 4px solid #9e9e9e;
}

.agent-card.working {
  border-left-color: #2196F3;
  background: #e3f2fd;
}

.agent-card.idle {
  border-left-color: #9e9e9e;
}

.agent-name {
  font-weight: bold;
  margin-bottom: 5px;
}

.agent-status {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 5px;
}

.agent-updated {
  font-size: 0.8rem;
  color: #999;
}

.logs-card {
  grid-column: 1 / -1;
}

.logs-container {
  max-height: 400px;
  overflow-y: auto;
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 15px;
  border-radius: 8px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
}

.log-entry {
  margin-bottom: 5px;
  display: flex;
  gap: 10px;
}

.log-time {
  color: #888;
}

.log-level {
  font-weight: bold;
}

.log-level.info {
  color: #4CAF50;
}

.log-level.error {
  color: #f44336;
}

.log-level.warning {
  color: #ff9800;
}

.log-message {
  flex: 1;
}
</style>
