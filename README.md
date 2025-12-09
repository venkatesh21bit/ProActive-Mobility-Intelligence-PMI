# ProActive Mobility Intelligence (PMI)

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.11-blue)
![React](https://img.shields.io/badge/react-18.3-blue)
![Status](https://img.shields.io/badge/status-production--ready-brightgreen)

**Autonomous Predictive Maintenance and Proactive Service Scheduling System**

A cutting-edge AI-powered platform for predictive vehicle maintenance, anomaly detection, and automated customer engagement using multi-agent architecture.

---

## 🚀 Features

### Core Capabilities
- ✅ **Real-time Telemetry Ingestion** - High-throughput vehicle data processing
- ✅ **AI-Powered Predictions** - XGBoost, PyTorch, Isolation Forest anomaly detection
- ✅ **Multi-Agent Architecture** - 6 autonomous agents powered by Ray
- ✅ **UEBA Analytics** - User Entity Behavior Analytics for fraud detection
- ✅ **Manufacturing Insights** - NLP-powered quality feedback analysis
- ✅ **Automated Alerts** - SMS/Voice notifications via Twilio
- ✅ **Web Dashboard** - React-based real-time monitoring
- ✅ **Mobile App** - React Native iOS/Android applications

### Technical Stack

**Backend:**
- FastAPI 0.109.0 - High-performance async API
- Ray 2.52.1 - Distributed agent orchestration
- PostgreSQL + TimescaleDB - Time-series data
- Redis 5.0 - Stream processing & caching
- MLflow - ML experiment tracking
- scikit-learn, XGBoost, PyTorch - ML models

**Frontend:**
- React 18.3 + Vite - Modern web framework
- Recharts - Data visualization
- Axios - API communication

**Mobile:**
- React Native 0.76.5
- Expo ~52.0 - Cross-platform development

---

## 📋 Prerequisites

### Development
- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- Redis 7+
- Docker (optional)

### Production
- Railway account (backend hosting)
- Vercel account (frontend hosting)
- Expo EAS account (mobile deployment)
- Twilio account (optional - for SMS/voice)

---

## 🛠️ Quick Start

### Backend Setup

```bash
# Clone repository
git clone https://github.com/venkatesh21bit/ProActive-Mobility-Intelligence-PMI.git
cd ProActive-Mobility-Intelligence-PMI/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Initialize database
python -c "from data.database import init_db; import asyncio; asyncio.run(init_db())"

# Start services
uvicorn api.ingestion_service:app --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit VITE_API_URL to point to backend

# Start development server
npm run dev
```

### Mobile Setup

```bash
cd mobile

# Install dependencies
npm install

# Start Expo
npm start

# Scan QR code with Expo Go app
```

---

## 🌐 Production Deployment

See [GCP_DEPLOYMENT.md](./GCP_DEPLOYMENT.md) for complete Google Cloud Platform deployment guide.

### Quick Deploy Commands

**Backend (Cloud Run):**
```bash
cd backend
gcloud builds submit --tag gcr.io/YOUR_VENDOR_PROJECT_ID/pmi-backend
gcloud run deploy pmi-backend --image gcr.io/YOUR_VENDOR_PROJECT_ID/pmi-backend --region us-central1
```

**Frontend (Cloud Storage + CDN):**
```bash
cd frontend
npm run build
gsutil -m cp -r dist/* gs://YOUR_VENDOR_PROJECT_ID-pmi-frontend/
```

**Or use the deployment script:**
```powershell
.\deploy-gcp.ps1
```

---

## 📊 Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                      Client Applications                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Web Dashboard│  │  Mobile App  │  │  API Clients │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          └──────────────────┴──────────────────┘
                             │
          ┌──────────────────▼────────────────────┐
          │       FastAPI Ingestion Service       │
          │  (CORS, Auth, Rate Limiting, GZip)    │
          └──────────────────┬────────────────────┘
                             │
          ┌──────────────────┴────────────────────┐
          │                                       │
    ┌─────▼─────┐                          ┌─────▼─────┐
    │   Redis   │                          │PostgreSQL │
    │  Streams  │                          │TimescaleDB│
    └─────┬─────┘                          └─────┬─────┘
          │                                       │
    ┌─────▼──────────────────────────────────────▼─────┐
    │            Ray Multi-Agent System                 │
    │  ┌──────────────────────────────────────────┐    │
    │  │         Master Orchestrator Agent         │    │
    │  └──────────────────┬───────────────────────┘    │
    │           ┌─────────┴─────────┐                  │
    │     ┌─────▼─────┐       ┌─────▼─────┐            │
    │     │Monitoring │       │Predictive │            │
    │     │  Agent    │       │ML Agent   │            │
    │     └───────────┘       └───────────┘            │
    │     ┌───────────┐       ┌───────────┐            │
    │     │Scheduling │       │Customer   │            │
    │     │  Agent    │       │Engagement │            │
    │     └───────────┘       └───────────┘            │
    │     ┌───────────┐                                │
    │     │ Quality   │                                │
    │     │ Insights  │                                │
    │     └───────────┘                                │
    └───────────────────────────────────────────────────┘
```

### Data Flow

1. **Telemetry Collection** → Vehicles send sensor data to API
2. **Stream Processing** → Redis Streams for real-time data
3. **Storage** → TimescaleDB for time-series analytics
4. **ML Processing** → Feature extraction, anomaly detection
5. **Agent Actions** → Predictive maintenance, scheduling, alerts
6. **Customer Engagement** → Automated SMS/voice notifications

---

## 🤖 Multi-Agent System

### Agents Overview

| Agent | Purpose | Technologies |
|-------|---------|--------------|
| **Master** | Orchestration, coordination | Ray, async scheduling |
| **Monitoring** | Real-time anomaly detection | Isolation Forest, One-Class SVM |
| **Predictive ML** | Failure prediction | XGBoost, PyTorch, tsfresh |
| **Scheduling** | Service appointment booking | Optimization algorithms |
| **Customer Engagement** | SMS/Voice notifications | Twilio API |
| **Quality Insights** | Manufacturing feedback | Sentence-Transformers, NLP |

---

## 📈 API Endpoints

### Health & Monitoring
- `GET /health` - Comprehensive health check
- `GET /readiness` - Kubernetes readiness probe
- `GET /liveness` - Kubernetes liveness probe
- `GET /monitoring/metrics/prometheus` - Prometheus metrics

### Telemetry Ingestion
- `POST /ingest` - Single telemetry record
- `POST /ingest/batch` - Batch ingestion (up to 1000 records)
- `GET /stream/info` - Redis stream statistics

### ML & Predictions
- `POST /predict/anomaly` - Anomaly detection
- `POST /predict/failure` - Failure prediction
- `GET /models/status` - ML model information

---

## 🔒 Security

### Best Practices Implemented
- ✅ Environment variables for secrets
- ✅ HTTPS enforced in production
- ✅ CORS restricted to known domains
- ✅ Rate limiting on all endpoints
- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ Input validation (Pydantic)
- ✅ JWT authentication ready
- ✅ Security headers (CSP, X-Frame-Options, etc.)
- ✅ Error messages sanitized in production

See [SECURITY.md](./SECURITY.md) for vulnerability reporting.

---

## 📊 Monitoring & Observability

### Metrics Available
- System metrics (CPU, memory, disk)
- Service metrics (uptime, requests, response times)
- Application metrics (predictions, anomalies, alerts)
- Database performance
- Redis stream lag

### Logging
- Structured JSON logging in production
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Centralized logging via Railway/Vercel

### Alerting
- Health check failures
- Database connection issues
- High error rates
- Performance degradation

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest --cov=. --cov-report=html

# Frontend tests
cd frontend
npm test

# E2E tests
npm run test:e2e
```

---

## 📚 Documentation

- [GCP Deployment Guide](./GCP_DEPLOYMENT.md)
- [Security Policy](./SECURITY.md)
- [Production Ready Status](./PRODUCTION_READY.md)
- [API Documentation](http://localhost:8000/docs) (dev mode)

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 👥 Team

- **Lead Developer** - [Your Name]
- **Contributors** - See [CONTRIBUTORS.md](./CONTRIBUTORS.md)

---

## 🙏 Acknowledgments

- Ray framework for distributed computing
- FastAPI for high-performance APIs
- React team for awesome frontend framework
- Expo for simplifying mobile development
- Open source community

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/venkatesh21bit/ProActive-Mobility-Intelligence-PMI/issues)
- **Discussions:** [GitHub Discussions](https://github.com/venkatesh21bit/ProActive-Mobility-Intelligence-PMI/discussions)
- **Email:** support@yourdomain.com

---

## 🗺️ Roadmap

### v1.1 (Q1 2026)
- [ ] GraphQL API
- [ ] Real-time WebSocket notifications
- [ ] Advanced analytics dashboard
- [ ] Fleet management features

### v1.2 (Q2 2026)
- [ ] Kubernetes deployment
- [ ] Multi-region support
- [ ] Enhanced ML models
- [ ] Driver behavior analytics

### v2.0 (Q3 2026)
- [ ] IoT device integration
- [ ] Blockchain for maintenance records
- [ ] AR/VR maintenance guides
- [ ] Carbon footprint tracking

---

**Made with ❤️ by the ProActive Mobility Team**

⭐ Star us on GitHub if this project helped you!
