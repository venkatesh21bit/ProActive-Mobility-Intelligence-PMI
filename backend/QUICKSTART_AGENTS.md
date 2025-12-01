# Quick Start Guide - Master + Worker Agents

## Prerequisites

1. **Redis** - Running (Railway or local)
2. **PostgreSQL** - Running (Railway or local)
3. **Python Environment** - Activated with all dependencies
4. **Ray** - Will auto-initialize when starting Master Agent

## Start the System (5 Steps)

### 1. Train ML Model (First Time Only)
```bash
cd backend
python ml/train_model.py
```
Expected: Model saved to `ml/models/anomaly_detection/`

### 2. Start Telemetry Simulator
```bash
cd backend
python simulators/telemetry_simulator.py
```
Expected: Running on http://localhost:8001

### 3. Start Ingestion Service
```bash
cd backend
python api/ingestion_service.py
```
Expected: Running on http://localhost:8000

### 4. Start ML Prediction Service
```bash
cd backend
python api/ml_service.py
```
Expected: Running on http://localhost:8002

### 5. Start Master Agent
```bash
cd backend
python -m agents
```
Expected: Ray initialized, listening for alerts

## Test the Complete Workflow

### Option 1: Run Test Suite
```bash
cd backend
python test_agents.py
```

This tests each agent individually:
- ✓ Diagnosis Agent
- ✓ Customer Engagement Agent
- ✓ Scheduling Agent
- ✓ Feedback Agent

### Option 2: Trigger Real Workflow

1. **Generate Alert**: Let simulator run for 30-60 seconds
2. **Check ML Service**: `curl http://localhost:8002/predict -X POST -H "Content-Type: application/json" -d '{"vehicle_id": 1}'`
3. **Verify Alert**: Check Redis stream `alerts:predicted`
4. **Monitor Master Agent**: Watch console for workflow execution

## Architecture Overview

```
Simulator → Ingestion → Redis Streams → ML Service → Alerts
                            ↓
                      Master Agent
                            ↓
        ┌──────────────────┼──────────────────┐
        ↓                  ↓                   ↓
   Diagnosis         Customer Eng.       Scheduling
        ↓                  ↓                   ↓
                      Feedback Agent
```

## Agent Endpoints

### Master Agent
- **Type**: Ray Actor (no HTTP endpoint)
- **Function**: Orchestration
- **Access**: Via Ray RPC or test script

### Worker Agents
All workers are Python classes called by Master Agent:
- `DiagnosisAgent.diagnose(prediction)`
- `CustomerEngagementAgent.initiate_contact(...)`
- `SchedulingAgent.find_available_slots(...)`
- `FeedbackAgent.collect_feedback(...)`

## Common Issues

### Ray Won't Start
```bash
# Kill existing Ray processes
ray stop
# Then restart Master Agent
python -m agents
```

### No Alerts Generated
1. Check telemetry simulator is running
2. Verify Redis connection
3. Check ML service logs
4. Ensure data is being ingested

### Agent Test Failures
- Ensure database migrations ran
- Check Railway credentials in `.env`
- Verify Redis and PostgreSQL are accessible

## Workflow States

| State                  | Description                          |
|------------------------|--------------------------------------|
| INITIATED              | Alert received, workflow started     |
| DIAGNOSED              | Component diagnosis complete         |
| CONTACTING_CUSTOMER    | Calling customer                     |
| SCHEDULING             | Finding appointment slots            |
| SCHEDULED              | Appointment confirmed                |
| CUSTOMER_DECLINED      | Customer declined service            |
| AWAITING_SERVICE       | Waiting for appointment date         |
| SERVICE_COMPLETED      | Service finished                     |
| FEEDBACK_COLLECTED     | Survey completed, labels updated     |
| ESCALATED              | Transferred to human                 |
| FAILED                 | Error in workflow                    |

## SLA Monitoring

Master Agent automatically tracks SLA compliance:

- **Critical**: Must schedule within 2 hours
- **High**: Must schedule within 24 hours
- **Medium**: Must schedule within 3 days
- **Low**: Must schedule within 1 week

## Next Steps

1. ✅ Test individual agents
2. ✅ Verify end-to-end workflow
3. ⏭️ Implement Manufacturing Quality Insights
4. ⏭️ Add UEBA module
5. ⏭️ Build frontend (React Native/PWA)

## Getting Help

- Check `agents/ARCHITECTURE.md` for detailed design
- Review `README.md` for full documentation
- Check agent logs for error details
- Use `test_agents.py` to isolate issues
