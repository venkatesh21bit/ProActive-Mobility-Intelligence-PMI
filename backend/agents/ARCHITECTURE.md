# Agent System Architecture

## Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         MASTER AGENT (Ray Actor)                     │
│                    Workflow Orchestration & SLA Management           │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
        ┌───────────▼────┐  ┌──────▼──────┐  ┌────▼────────┐
        │   Diagnosis    │  │  Customer   │  │ Scheduling  │
        │     Agent      │  │ Engagement  │  │    Agent    │
        └────────────────┘  └─────────────┘  └─────────────┘
                                    │
                            ┌───────▼──────┐
                            │  Feedback    │
                            │    Agent     │
                            └──────────────┘
```

## Data Flow

```
1. Vehicle Telemetry
   └─> Data Analysis Agent (ML Prediction)
       └─> Redis Stream: alerts:predicted
           └─> MASTER AGENT
               │
               ├─> Diagnosis Agent
               │   └─> Component Mapping + Cost/Time Estimation
               │
               ├─> Scheduling Agent  
               │   └─> Find Available Slots
               │
               ├─> Customer Engagement Agent
               │   └─> Twilio Voice Call → Customer Response
               │       │
               │       ├─> Accept → Create Appointment
               │       ├─> Decline → Archive
               │       └─> Unclear → Escalate to Human
               │
               └─> [After Service Completion]
                   └─> Feedback Agent
                       └─> Survey + Label Updates → Model Retraining
```

## Agent Details

### Master Agent
- **Technology**: Ray remote actor
- **Responsibilities**:
  - Listen to `alerts:predicted` stream
  - Coordinate worker agents
  - Maintain workflow state
  - Enforce SLA deadlines
  - Audit logging
- **State Management**: In-memory workflows dict
- **Communication**: Ray RPC to worker agents

### Worker Agents

#### 1. Diagnosis Agent
- **Input**: ML prediction (severity, features, probability)
- **Output**: Component diagnosis, repair actions, cost/time estimates
- **Logic**: Rule-based mapping from symptoms to components
- **Components Covered**: 50+ (Engine, Oil, Vibration, Battery, Fuel)

#### 2. Customer Engagement Agent
- **Input**: Diagnosis + available slots
- **Output**: Conversation result (accepted/declined/escalated)
- **Features**:
  - Template-based greeting scripts
  - Intent classification NLU
  - Multi-turn conversation state
  - Human escalation on confusion/request
- **Integration**: Twilio Programmable Voice (production structure ready)

#### 3. Scheduling Agent
- **Input**: Customer info, diagnosis, urgency
- **Output**: Available appointment slots + booking confirmation
- **Features**:
  - Business hours: 8 AM - 6 PM
  - Conflict detection
  - Capacity management
  - Urgency-based scheduling
- **Database**: `appointments`, `service_centers` tables

#### 4. Feedback Agent
- **Input**: Service completion event
- **Output**: Survey responses + updated prediction labels
- **Features**:
  - 6-question customer survey
  - Outcome classification (5 types)
  - Prediction accuracy tracking
  - Training data export
- **ML Loop**: Labels → Model Retraining

## SLA Constraints

| Urgency   | Severity | Time Window | Use Case                    |
|-----------|----------|-------------|-----------------------------|
| Immediate | Critical | 2 hours     | Engine failure, no start    |
| Urgent    | High     | 24 hours    | Overheating, oil pressure   |
| Soon      | Medium   | 3 days      | Battery degradation         |
| Routine   | Low      | 1 week      | Preventive maintenance      |

## Communication Patterns

### Event-Driven (Redis Streams)
- `alerts:predicted` - ML predictions
- `alerts:*` - Various alert types
- Consumer groups for scalability

### RPC (Ray)
- Master → Worker: Direct method invocation
- Synchronous for workflow control
- Asynchronous for background tasks

### Database (PostgreSQL)
- Appointments
- Maintenance records
- Failure predictions (with actual outcomes)
- Audit logs
- Customer/Vehicle data

## Error Handling

1. **Retry Logic**: 3 retries with exponential backoff
2. **Human Escalation**: On customer request or 3+ unclear responses
3. **SLA Violation**: Alert human operator
4. **Agent Failure**: Logged to audit trail for UEBA analysis

## Example Workflow

```
Time    Event
-----   -----
00:00   Vehicle VEH_001 sends telemetry (high engine temp)
00:01   Data Analysis Agent predicts 85% failure probability
00:02   Alert published to alerts:predicted stream
00:03   Master Agent receives alert
00:04   Diagnosis Agent → "Thermostat failure, $450, 3.5h"
00:05   Scheduling Agent → Finds 5 slots in next 24h
00:06   Customer Engagement → Initiates Twilio call
00:08   Customer accepts Option 1 (tomorrow 9 AM)
00:09   Scheduling Agent → Creates appointment APT-000042
00:10   SLA Check → Within 24h window ✓
...
24:00   Service completed → Thermostat replaced
24:30   Feedback Agent → Surveys customer
24:35   Customer rates 5/5, confirms accurate prediction
24:36   Feedback Agent → Updates prediction labels
24:37   Labeled data exported for next training cycle
```

## Scaling Considerations

- **Ray Cluster**: Scale worker agents horizontally
- **Redis Streams**: Consumer groups for parallel processing
- **Database**: Read replicas for heavy queries
- **Twilio**: Concurrent call limits (production plan needed)

## Security

- Redis authentication
- PostgreSQL role-based access
- Audit logging (all agent actions)
- UEBA (detect anomalous agent behavior)
- Call recording consent (compliance)
