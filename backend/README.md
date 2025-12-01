# ProActive Mobility Intelligence (PMI)
## Autonomous Predictive Maintenance System

A multi-agent system for proactive vehicle maintenance prediction, autonomous service scheduling, and manufacturing quality feedback loop.

## 🏗️ Project Structure

```
backend/
├── agents/              # Agent implementations (Master, Data Analysis, Diagnosis, etc.)
├── api/                 # FastAPI services
│   └── ingestion_service.py  # Telemetry ingestion API
├── config/              # Configuration management
│   └── settings.py      # Environment settings
├── data/                # Data models and database
│   ├── models.py        # SQLAlchemy models
│   ├── database.py      # Database connection
│   ├── redis_client.py  # Redis Streams client
│   └── stream_consumer.py  # Telemetry consumer
├── infrastructure/      # Docker & monitoring configs
│   ├── init-scripts/    # Database initialization
│   ├── prometheus.yml   # Prometheus config
│   └── grafana-datasources.yml  # Grafana config
├── ml/                  # Machine learning models
├── simulators/          # Data generators
│   └── telemetry_simulator.py  # Vehicle telemetry simulator
├── tests/               # Test suite
├── docker-compose.yml   # Infrastructure services
├── requirements.txt     # Python dependencies
└── .env.example         # Environment template
```

## 🚀 Tech Stack

- **Backend Framework**: FastAPI (async Python)
- **Agent Orchestration**: Ray (actors + Serve)
- **Messaging**: Redis Streams
- **Time-Series DB**: TimescaleDB (PostgreSQL extension)
- **Relational DB**: PostgreSQL
- **Object Storage**: MinIO (S3-compatible)
- **ML Framework**: PyTorch, scikit-learn, XGBoost
- **MLOps**: MLflow
- **Monitoring**: Prometheus + Grafana
- **Containerization**: Docker Compose

## 📋 Prerequisites

- Python 3.11+
- Docker & Docker Compose (optional - for local infrastructure)
- Git

## 📚 Documentation

- **[README.md](README.md)** - This file: Architecture & setup overview
- **[QUICKSTART_AGENTS.md](QUICKSTART_AGENTS.md)** - Quick start guide for agents
- **[ML_TRAINING_GUIDE.md](ML_TRAINING_GUIDE.md)** - Complete ML training documentation
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - ⚠️ **Common issues and solutions**
- **[agents/ARCHITECTURE.md](agents/ARCHITECTURE.md)** - Detailed agent architecture
- **[SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md)** - Complete system visualization

## 🛠️ Setup Instructions

### 1. Clone Repository

```bash
cd backend
```

### 2. Create Environment File

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Start Infrastructure Services

```bash
docker-compose up -d
```

This starts:
- **TimescaleDB** (PostgreSQL + TimescaleDB): `localhost:5432`
- **Redis**: `localhost:6379`
- **MinIO**: `localhost:9000` (console: `localhost:9001`)
- **MLflow**: `localhost:5000`
- **Prometheus**: `localhost:9090`
- **Grafana**: `localhost:3000` (admin/admin123)

### 4. Install Python Dependencies

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

### 5. Initialize Database

The database schema is automatically initialized via Docker init scripts. To verify:

```bash
# Connect to database
docker exec -it pmi_timescaledb psql -U pmi_user -d pmi_db

# Check tables
\dt
```

## 🏃 Running the Services

### Start Telemetry Simulator

Generates sensor data for 10 vehicles:

```bash
cd simulators
python telemetry_simulator.py
```

Access:
- HTTP API: http://localhost:8001
- WebSocket: ws://localhost:8001/ws
- Docs: http://localhost:8001/docs

### Start Ingestion Service

Receives telemetry and writes to Redis + TimescaleDB:

```bash
cd api
python ingestion_service.py
```

Access:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

### Train ML Model (First Time)

Before running the ML service, train the model:

```bash
cd ml
python train_model.py
```

This will:
- Generate 100 vehicles of synthetic training data
- Extract features using rolling statistics and domain knowledge
- Train Isolation Forest + XGBoost ensemble
- Log experiment to MLflow
- Save model to `ml/models/anomaly_detection/`

### Start ML Prediction Service

Serves ML predictions via API:

```bash
cd api
python ml_service.py
```

Access:
- API: http://localhost:8002
- Docs: http://localhost:8002/docs
- Model Info: http://localhost:8002/model/info

### Start Stream Consumer

Processes telemetry in real-time:

```bash
cd data
python stream_consumer.py
```

## 🧪 Testing the Pipeline

### 1. Check Simulator

```bash
# Get all vehicles
curl http://localhost:8001/vehicles

# Get telemetry for all vehicles
curl http://localhost:8001/telemetry

# Get specific vehicle telemetry
curl http://localhost:8001/telemetry/VEH_001
```

### 2. Ingest Telemetry

```bash
# Get telemetry from simulator
curl http://localhost:8001/telemetry > telemetry.json

# Send to ingestion service
curl -X POST http://localhost:8000/ingest/batch \
  -H "Content-Type: application/json" \
  -d @telemetry.json

# Check ingestion stats
curl http://localhost:8000/stats
```

### 3. Verify Data in TimescaleDB

```bash
docker exec -it pmi_timescaledb psql -U pmi_user -d pmi_db

SELECT COUNT(*) FROM vehicle_telemetry;
SELECT * FROM vehicle_telemetry ORDER BY time DESC LIMIT 5;
```

### 4. Check Redis Streams

```bash
docker exec -it pmi_redis redis-cli -a redis_password

XINFO STREAM vehicle:telemetry
XLEN vehicle:telemetry
XREAD COUNT 1 STREAMS vehicle:telemetry 0
```

## 📊 Monitoring

### Grafana Dashboards

Access Grafana at http://localhost:3000 (admin/admin123)

Pre-configured datasources:
- Prometheus (metrics)
- TimescaleDB (telemetry data)

### Prometheus Metrics

http://localhost:9090

### MLflow Tracking

http://localhost:5000

## 🗄️ Database Schema

### Key Tables

- `vehicle_telemetry` - Time-series sensor data (hypertable)
- `vehicles` - Vehicle registry
- `customers` - Customer information
- `appointments` - Service appointments
- `failure_predictions` - ML model predictions (hypertable)
- `rca_capa_records` - Root cause analysis records
- `maintenance_records` - Service history
- `agent_audit_log` - Agent activity for UEBA (hypertable)

## 🤖 Agent Architecture

### Overview

The system uses Ray for distributed agent orchestration:

```
Master Agent (Ray Actor) - Orchestrates workflow, manages SLA
    ├── Diagnosis Agent - Component-level diagnostics
    ├── Customer Engagement Agent - Twilio voice + NLU
    ├── Scheduling Agent - Appointment slot management
    └── Feedback Agent - Post-service surveys + label updates
```

### Agent Descriptions

#### 1. **Master Agent** (`agents/master_agent.py`)
- Listens to `alerts:predicted` Redis stream
- Orchestrates all worker agents via Ray RPC
- Maintains workflow state and conversation context
- Enforces SLA constraints (immediate: 2h, urgent: 24h, routine: 1 week)
- Audit logging for compliance and UEBA

**SLA Constraints:**
- Critical/Immediate: 2 hours
- High/Urgent: 24 hours  
- Medium/Soon: 72 hours
- Low/Routine: 168 hours

#### 2. **Data Analysis Agent** (`agents/data_analysis_agent.py`)
- Real-time failure prediction using ML ensemble
- Feature extraction (50+ statistical + domain features)
- Severity classification (critical/high/medium/low/normal)
- Publishes alerts to Redis stream

#### 3. **Diagnosis Agent** (`agents/diagnosis_agent.py`)
- Maps ML predictions to specific components
- Identifies failure modes and symptoms
- Generates repair action lists
- Estimates cost and downtime
- **Coverage**: Engine (thermostat, water pump, radiator), Oil system, Vibration (mounts, balance, driveshaft), Battery, Fuel system

#### 4. **Customer Engagement Agent** (`agents/customer_engagement_agent.py`)
- Twilio Programmable Voice integration (production-ready)
- Template-based NLU with intent classification
- Multi-turn conversation management
- Human escalation on request or confusion
- Consent recording for compliance

**Conversation Flow:**
1. Greeting with urgency messaging
2. Diagnosis explanation
3. Appointment slot proposal
4. Response handling (accept/decline/alternative)
5. Confirmation or escalation

#### 5. **Scheduling Agent** (`agents/scheduling_agent.py`)
- Service center capacity management
- Available slot generation (business hours: 8 AM - 6 PM)
- Conflict detection and resolution
- Urgency-based scheduling windows
- Appointment CRUD operations
- Rescheduling support

#### 6. **Feedback Agent** (`agents/feedback_agent.py`)
- Post-service follow-up survey (6 questions)
- Service outcome classification
- Prediction accuracy tracking
- Maintenance record creation
- Training label updates for model improvement
- Feedback analytics and reporting
- Export labeled data for retraining

#### 7. **Manufacturing Quality Insights** (Coming Next)
- NLP-based RCA/CAPA analysis
- Semantic similarity search (sentence transformers)
- Failure pattern correlation
- Design improvement recommendations

### Running Agents

#### Start Master Agent
```bash
python -m agents.master_agent
# Or use: run_master_agent.bat
```

#### Test All Agents
```bash
python test_agents.py
# Or use: test_agents.bat
```

### Agent Workflow Example

1. **Alert**: ML service detects 85% failure probability for vehicle VEH_001
2. **Master Agent**: Receives alert from Redis `alerts:predicted` stream
3. **Diagnosis Agent**: Maps to "Thermostat failure", estimates $450, 3.5 hours
4. **Scheduling Agent**: Finds 5 available slots in next 24 hours (urgent SLA)
5. **Customer Engagement**: Initiates Twilio call with personalized script
6. **Customer**: Responds "yes, option 1" (accepts first slot)
7. **Scheduling Agent**: Creates appointment record, confirmation #APT-000042
8. **SLA Check**: Appointment within 24h deadline ✓
9. **Service Complete**: Technician confirms repair (thermostat replaced)
10. **Feedback Agent**: Surveys customer, updates prediction labels
11. **Model Improvement**: Exports labeled data for next training cycle

## 🔐 Security Features

- Redis password authentication
- PostgreSQL role-based access
- JWT tokens for API authentication (to be implemented)
- Agent audit logging for UEBA
- Anomaly detection on agent behavior

## 📝 Development

### Code Style

```bash
black .
flake8 .
mypy .
```

### Run Tests

```bash
pytest tests/ -v --cov=.
```

## 🚧 Roadmap

- [x] Infrastructure setup (Docker Compose)
- [x] Database schema (TimescaleDB + PostgreSQL)
- [x] Telemetry simulator (10 vehicles, WebSocket/HTTP)
- [x] Ingestion service (FastAPI → Redis Streams + TimescaleDB)
- [x] Stream consumer (real-time processing)
- [x] ML prediction core (Isolation Forest + XGBoost ensemble)
- [x] Feature extraction (rolling stats, domain features)
- [x] Data Analysis Agent
- [x] MLflow integration for experiment tracking
- [x] FastAPI ML serving endpoint
- [x] **Master Agent** (Ray-based orchestration, SLA management)
- [x] **Diagnosis Agent** (component mapping, cost/downtime estimation)
- [x] **Customer Engagement Agent** (Twilio + NLU conversations)
- [x] **Scheduling Agent** (appointment slot management)
- [x] **Feedback Agent** (post-service surveys, label updates)
- [ ] Manufacturing Quality Insights (NLP-based RCA/CAPA analysis)
- [ ] UEBA module (agent behavior anomaly detection)
- [ ] Frontend (React Native/PWA)
- [ ] Production deployment (Kubernetes + ArgoCD)

## 📄 License

MIT License

## 👥 Contributors

Built for autonomous predictive maintenance and proactive service scheduling.
