# Quick Start Guide - Orkestron

## 🚀 Get Started in 5 Minutes

### Step 1: Setup Environment

**Windows:**
```bash
# Run the setup script
setup.bat

# Or manually:
cd backend
pip install -r requirements.txt

cd ../frontend/dashboard
npm install

cd ../vue-monitor
npm install
```

### Step 2: Configure API Key

Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=sk-your-api-key-here
```

Get a free API key at: https://platform.openai.com

### Step 3: Start Infrastructure

```bash
# Start Redis and RabbitMQ
docker-compose up -d redis rabbitmq

# Verify they're running
docker ps
```

### Step 4: Run the System

**Option A: Run with Python directly**
```bash
# Start backend API
cd backend
uvicorn api.routes:app --reload --port 8000

# In another terminal, start main cycle
cd ..
python main.py
```

**Option B: Run with Docker**
```bash
docker-compose up -d
```

### Step 5: Access Dashboards

- **Main Dashboard**: http://localhost:3000
- **Vue Monitor**: http://localhost:3001
- **API Documentation**: http://localhost:8000/docs
- **RabbitMQ Admin**: http://localhost:15672 (admin/admin)

## 📋 Common Commands

### Run Tests
```bash
cd tests
pytest test_suite.py -v
```

### View Logs
```bash
# Application logs
tail -f logs/swarmai.log

# Docker logs
docker-compose logs -f
```

### Restart Services
```bash
docker-compose restart
```

### Stop Everything
```bash
docker-compose down
```

## 🎯 Using the System

### Submit a Task via API

```bash
curl -X POST http://localhost:8000/tasks/submit \
  -H "Content-Type: application/json" \
  -d '{
    "requirements": "Build a todo app with user authentication",
    "project_type": "web_application"
  }'
```

### Check Agent Status

```bash
curl http://localhost:8000/agents/status
```

### Start a Cycle

```bash
curl -X POST http://localhost:8000/cycle/start
```

## 🔧 Troubleshooting

### Redis Not Connecting
```bash
docker-compose restart redis
# Check if running
docker ps | grep redis
```

### RabbitMQ Issues
```bash
docker-compose restart rabbitmq
# Access management UI
open http://localhost:15672
```

### Python Import Errors
```bash
cd backend
pip install -e .
```

### Frontend Won't Start
```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

## 📊 Monitoring

### Check System Health
```bash
curl http://localhost:8000/health
```

### View Metrics
```bash
curl http://localhost:8000/metrics
```

### View Recent Logs
```bash
curl http://localhost:8000/logs?limit=50
```

## 🎓 Next Steps

1. **Read the full README** - Understand the architecture
2. **Explore the API docs** - http://localhost:8000/docs
3. **Submit your first task** - Use the dashboard or API
4. **Monitor agent activity** - Watch the real-time dashboards
5. **Customize settings** - Edit `config/settings.yaml`

## 💡 Tips

- Start with simple tasks to understand the flow
- Monitor the logs to see agent activities
- Use the manual override buttons in the dashboard
- Check RabbitMQ queue for pending tasks
- Review generated code in `generated_code/` folder

## 🆘 Need Help?

- Check logs: `logs/swarmai.log`
- Review test suite: `tests/test_suite.py`
- Read API docs: http://localhost:8000/docs
- Check configuration: `config/settings.yaml`

---

Happy Building! 🚀
