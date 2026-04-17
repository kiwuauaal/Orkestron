# Orkestron

Multi-agent orchestration system with central AI coordinator and GUI for autonomous full-stack development.

## Architecture

- **Central Orchestrator**: Task assignment, coordination, decision-making using free-tier LLMs
- **5 Specialized Agents**: Planner, Builder, Tester, Guard, Designer
- **Web Dashboard**: Real-time monitoring, task board, logs, manual override
- **Message Bus**: Redis Pub/Sub + RabbitMQ for agent communication
- **Shared Memory**: State management with agent-local context
- **30-Minute Autonomous Cycles**: Trigger → Check → Brain → Build → Guard → Sleep

## Features

- 🤖 **Multi-Agent Swarm**: 5 specialized agents working together
- 🎯 **Central Orchestration**: AI-powered task assignment and coordination
- 📊 **Real-Time Dashboard**: Monitor agent status, tasks, and logs
- 🔄 **Autonomous Cycles**: 30-minute execution cycles
- 🛡️ **Quality Gates**: Automated testing and security checks
- 💬 **Dual Message Bus**: Redis + RabbitMQ for reliable communication
- 🌐 **Public API Integration**: Access to 1000+ free APIs

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Redis
- RabbitMQ
- OpenAI API key (free tier works)

### Installation

1. **Clone the repository**
```bash
cd "ai bot project"
```

2. **Install backend dependencies**
```bash
cd backend
pip install -r requirements.txt
```

3. **Install frontend dependencies**
```bash
cd frontend/dashboard
npm install

cd ../vue-monitor
npm install
```

4. **Set environment variables**
```bash
# Create .env file
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

5. **Start infrastructure (Redis & RabbitMQ)**
```bash
docker-compose up -d redis rabbitmq
```

6. **Run the backend**
```bash
cd backend
uvicorn api.routes:app --reload --port 8000
```

7. **Run the frontend dashboard**
```bash
cd frontend/dashboard
npm run dev
```

8. **Run the Vue monitor**
```bash
cd frontend/vue-monitor
npm run dev
```

## Using Docker

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## System Components

### Backend (FastAPI)
- **Orchestrator**: Central AI coordinator
- **Agents**: Planner, Builder, Tester, Guard, Designer
- **Message Bus**: Redis + RabbitMQ
- **Shared State**: Redis-based state management
- **API**: REST + WebSocket endpoints

### Frontend
- **Dashboard** (Next.js): Main control panel
- **Monitor** (Vue.js): Real-time metrics viewer

## API Endpoints

- `POST /tasks` - Create new task
- `GET /tasks/pending` - Get pending tasks
- `POST /tasks/submit` - Submit requirements
- `GET /agents/status` - Get agent status
- `GET /cycle/status` - Get cycle status
- `GET /metrics` - Get all metrics
- `GET /logs` - Get system logs
- `WS /ws` - WebSocket for real-time updates

## Testing

Run the complete test suite (47 tests):

```bash
cd tests
pytest test_suite.py -v
```

## Configuration

Edit `config/settings.yaml` to customize:
- Cycle interval (default: 30 minutes)
- Agent configurations
- Message bus settings
- Monitoring ports
- Test suite requirements

## Project Structure

```
ai-bot-project/
├── backend/
│   ├── orchestrator/          # Central AI coordinator
│   ├── agents/                # 5 specialized agents
│   │   ├── planner/
│   │   ├── builder/
│   │   ├── tester/
│   │   ├── guard/
│   │   └── designer/
│   ├── message_bus/           # Redis + RabbitMQ
│   ├── shared_memory/         # State management
│   ├── cycle_manager/         # 30-min cycle execution
│   └── api/                   # REST/WebSocket endpoints
├── frontend/
│   ├── dashboard/             # Next.js web UI
│   └── vue-monitor/           # Vue.js monitoring
├── config/                    # Configuration files
├── logs/                      # Centralized logging
├── tests/                     # Test suite (47 tests)
├── deployment/                # Deployment scripts
└── main.py                    # Entry point
```

## Agent Responsibilities

1. **Planner**: Analyze requirements and break into executable tasks
2. **Builder**: Generate backend/frontend code
3. **Tester**: Quality assurance and bug detection
4. **Guard**: Security scanning and quality gates
5. **Designer**: UI/UX component generation

## Cycle Phases

1. **Trigger**: Wake and initialize cycle
2. **Check**: Scan and validate pending tasks
3. **Brain**: Plan and assign tasks to agents
4. **Build**: Execute tasks (database, backend, pages, tests, deploy)
5. **Guard**: Run quality checks (lint, type, security, secrets, tests)
6. **Sleep**: Log results and rest until next cycle

## Cost Optimization

- Uses free-tier LLM APIs
- Public APIs integration (1000+ free APIs)
- Efficient resource utilization
- Max 5 parallel agents

## Monitoring

Access the dashboards:
- **Main Dashboard**: http://localhost:3000
- **Vue Monitor**: http://localhost:3001
- **API Docs**: http://localhost:8000/docs
- **RabbitMQ Management**: http://localhost:15672

## Troubleshooting

### Redis connection issues
```bash
docker-compose restart redis
```

### RabbitMQ connection issues
```bash
docker-compose restart rabbitmq
```

### Check logs
```bash
tail -f logs/swarmai.log
```

## License

This project is **open source** and available under the [MIT License](LICENSE).

You are free to:
- ✅ Use this software for commercial purposes
- ✅ Modify the code
- ✅ Distribute copies
- ✅ Use the software privately

Under these conditions:
- Include the original copyright notice
- Include the license notice in all copies

## Contributing

Contributions are welcome! This is an open source project and we encourage community contributions.

Please read our contributing guidelines before submitting pull requests.

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

For issues or contributions:
- 📝 Open an issue on GitHub
- ⭐ Star the repository if you find it helpful
