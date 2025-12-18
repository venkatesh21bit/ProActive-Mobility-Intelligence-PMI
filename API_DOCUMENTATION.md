# API Documentation

## Base URL
Production: `https://pmi-backend-418022813675.us-central1.run.app`

## Authentication

All protected endpoints require JWT authentication via Bearer token.

```http
Authorization: Bearer <access_token>
```

## Endpoints

### Authentication

#### Register New Customer
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "customer@example.com",
  "password": "secure_password",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "address": "123 Main St" (optional)
}

Response: 201 Created
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "customer_id": 1,
  "email": "customer@example.com",
  "role": "customer"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "customer@example.com",
  "password": "secure_password"
}

Response: 200 OK
{
  "customer_id": 1,
  "first_name": "John",
  "last_name": "Doe",
  "email": "customer@example.com",
  "phone": "+1234567890",
  "vehicle": {
    "vehicle_id": 1,
    "vin": "HERO1234567890123",
    "make": "Hero MotoCorp",
    "model": "Splendor",
    "year": 2023,
    "mileage": 5000
  },
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

#### Refresh Token
```http
POST /api/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ..."
}

Response: 200 OK
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "customer_id": 1,
  "email": "customer@example.com",
  "role": "customer"
}
```

#### Get Current User
```http
GET /api/auth/me
Authorization: Bearer <token>

Response: 200 OK
{
  "customer_id": 1,
  "first_name": "John",
  "last_name": "Doe",
  "email": "customer@example.com",
  "phone": "+1234567890",
  "address": "123 Main St",
  "vehicles": [...]
}
```

#### Logout
```http
POST /api/auth/logout
Authorization: Bearer <token>

Response: 200 OK
{
  "message": "Successfully logged out"
}
```

### Bookings

#### Create Booking
```http
POST /api/bookings/create
Authorization: Bearer <token>
Content-Type: application/json

{
  "customer_id": 1,
  "vehicle_id": 1,
  "service_type": "regular_service",
  "preferred_date": "2024-12-25",
  "preferred_time": "10:00"
}

Response: 200 OK
{
  "appointment_id": 1,
  "customer_id": 1,
  "vehicle_id": 1,
  "scheduled_time": "2024-12-25T10:00:00",
  "appointment_type": "regular_service",
  "status": "scheduled",
  "service_center": {
    "center_id": 1,
    "name": "Hero Service Center",
    "address": "..."
  }
}
```

#### Get Customer Bookings
```http
GET /api/bookings/customer/{customer_id}
Authorization: Bearer <token>

Response: 200 OK
[
  {
    "appointment_id": 1,
    "vehicle_id": 1,
    "scheduled_time": "2024-12-25T10:00:00",
    "appointment_type": "regular_service",
    "status": "scheduled"
  }
]
```

### Monitoring

#### Health Check
```http
GET /monitoring/health

Response: 200 OK
{
  "status": "healthy",
  "timestamp": "2024-12-17T12:00:00Z",
  "environment": "production",
  "version": "2.0.0",
  "checks": {
    "database": "healthy",
    "redis": "healthy"
  },
  "uptime_seconds": 86400
}
```

#### System Metrics
```http
GET /monitoring/metrics

Response: 200 OK
{
  "cpu_percent": 25.5,
  "memory_percent": 45.2,
  "memory_used_mb": 512.5,
  "memory_total_mb": 2048.0,
  "disk_percent": 35.0,
  "disk_used_gb": 7.5,
  "disk_total_gb": 20.0,
  "active_connections": 5,
  "timestamp": "2024-12-17T12:00:00Z"
}
```

#### Database Statistics
```http
GET /monitoring/stats/database

Response: 200 OK
{
  "total_customers": 150,
  "total_vehicles": 200,
  "total_appointments": 500,
  "total_telemetry_records": 1000000,
  "database_size_mb": 512.5,
  "active_connections": 10
}
```

### Dashboard

#### Get All Vehicles
```http
GET /api/dashboard/vehicles
Authorization: Bearer <token>

Response: 200 OK
[
  {
    "vehicle_id": 1,
    "vin": "HERO1234567890123",
    "make": "Hero MotoCorp",
    "model": "Splendor",
    "year": 2023,
    "mileage": 5000,
    "customer_id": 1
  }
]
```

#### Get Vehicle Details
```http
GET /api/dashboard/vehicle/{vehicle_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "vehicle_id": 1,
  "vin": "HERO1234567890123",
  "make": "Hero MotoCorp",
  "model": "Splendor",
  "year": 2023,
  "mileage": 5000,
  "health_score": 85.5,
  "recent_telemetry": [...],
  "maintenance_records": [...],
  "predictions": [...]
}
```

## Error Responses

All errors follow this format:

```json
{
  "error": "Error Type",
  "message": "Detailed error message",
  "request_id": "uuid-v4",
  "detail": "Additional details" (optional)
}
```

### HTTP Status Codes

- `200 OK` - Success
- `201 Created` - Resource created
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Missing or invalid token
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

### Rate Limiting

- Default: 120 requests per minute per IP
- Headers included in response:
  - `X-RateLimit-Limit`: Maximum requests per minute
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Unix timestamp when limit resets

Example:
```http
X-RateLimit-Limit: 120
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1702819200
```

When rate limit exceeded:
```json
{
  "error": "Rate limit exceeded",
  "message": "Maximum 120 requests per minute allowed",
  "retry_after": 60
}
```

## Request/Response Headers

### Required Request Headers
```http
Content-Type: application/json
Accept: application/json
Authorization: Bearer <token> (for protected endpoints)
```

### Response Headers
```http
Content-Type: application/json
X-Request-ID: <uuid>
X-RateLimit-Limit: 120
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1702819200
```

## Pagination

For list endpoints that support pagination:

```http
GET /api/resource?page=1&limit=20

Response:
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "pages": 5
  }
}
```

## Filtering

Many endpoints support filtering:

```http
GET /api/vehicles?make=Hero&year=2023
GET /api/appointments?status=scheduled&start_date=2024-01-01
```

## Sorting

Use `sort` parameter:

```http
GET /api/vehicles?sort=year:desc,mileage:asc
```

## Field Selection

Use `fields` parameter to select specific fields:

```http
GET /api/vehicles?fields=vin,make,model
```

## Testing

### Postman Collection
Import the Postman collection for easy testing: [Download](./postman_collection.json)

### cURL Examples

Register:
```bash
curl -X POST https://api.example.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","first_name":"Test","last_name":"User","phone":"+1234567890"}'
```

Login:
```bash
curl -X POST https://api.example.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

Create Booking:
```bash
curl -X POST https://api.example.com/api/bookings/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"customer_id":1,"vehicle_id":1,"service_type":"regular_service","preferred_date":"2024-12-25","preferred_time":"10:00"}'
```

## WebSocket Support

(Coming soon)

## Webhooks

(Coming soon)

## SDK/Client Libraries

- Python: (Coming soon)
- JavaScript/TypeScript: (Coming soon)
- Mobile (React Native): Built-in in mobile app

## Changelog

### v2.0.0 (2024-12-17)
- Added JWT authentication
- Implemented RBAC
- Added rate limiting
- Enhanced error handling
- Added comprehensive monitoring
- Performance optimizations

### v1.0.0 (2024-11-01)
- Initial release
- Basic authentication
- Booking system
- Vehicle management

## Support

- API Issues: https://github.com/yourorg/pmi/issues
- Email: support@example.com
- Docs: https://docs.example.com
