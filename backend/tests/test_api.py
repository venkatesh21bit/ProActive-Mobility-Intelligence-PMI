"""
Backend Unit Tests
"""

import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from api.ingestion_service import app
from data.database import Base, get_db_session
from data.models import Customer, Vehicle
from auth.security import create_access_token, get_password_hash

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db"

# Create test engine and session
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session():
    """Create a fresh database session for each test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
async def client(db_session):
    """Create test client with overridden database session."""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db_session] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def test_customer(db_session):
    """Create a test customer."""
    customer = Customer(
        first_name="Test",
        last_name="User",
        email="test@example.com",
        password_hash=get_password_hash("testpassword"),
        phone="+1234567890",
        role="customer"
    )
    db_session.add(customer)
    await db_session.commit()
    await db_session.refresh(customer)
    return customer


@pytest.fixture
async def test_vehicle(db_session, test_customer):
    """Create a test vehicle."""
    vehicle = Vehicle(
        vin="TEST1234567890123",
        customer_id=test_customer.customer_id,
        make="Hero MotoCorp",
        model="Splendor",
        year=2023,
        mileage=5000
    )
    db_session.add(vehicle)
    await db_session.commit()
    await db_session.refresh(vehicle)
    return vehicle


@pytest.fixture
def auth_token(test_customer):
    """Generate auth token for test customer."""
    return create_access_token(data={
        "sub": str(test_customer.customer_id),
        "email": test_customer.email,
        "role": test_customer.role
    })


# Test Cases

@pytest.mark.asyncio
async def test_health_check(client):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "checks" in data


@pytest.mark.asyncio
async def test_register_customer(client):
    """Test customer registration."""
    response = await client.post("/api/auth/register", json={
        "email": "new@example.com",
        "password": "password123",
        "first_name": "New",
        "last_name": "User",
        "phone": "+1234567890"
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["email"] == "new@example.com"


@pytest.mark.asyncio
async def test_login(client, test_customer):
    """Test customer login."""
    response = await client.post("/api/auth/login", json={
        "email": test_customer.email,
        "password": "testpassword"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["email"] == test_customer.email


@pytest.mark.asyncio
async def test_login_invalid_password(client, test_customer):
    """Test login with invalid password."""
    response = await client.post("/api/auth/login", json={
        "email": test_customer.email,
        "password": "wrongpassword"
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(client, test_customer, auth_token):
    """Test getting current user info."""
    response = await client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_customer.email


@pytest.mark.asyncio
async def test_unauthorized_access(client):
    """Test accessing protected endpoint without token."""
    response = await client.get("/api/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_booking(client, test_customer, test_vehicle, auth_token):
    """Test creating a booking."""
    response = await client.post(
        "/api/bookings/create",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "customer_id": test_customer.customer_id,
            "vehicle_id": test_vehicle.vehicle_id,
            "service_type": "regular_service",
            "preferred_date": "2024-12-25",
            "preferred_time": "10:00"
        }
    )
    assert response.status_code in [200, 201]


@pytest.mark.asyncio
async def test_rate_limiting(client):
    """Test rate limiting middleware."""
    # Make many requests rapidly
    responses = []
    for _ in range(150):
        response = await client.get("/health")
        responses.append(response.status_code)
    
    # Should hit rate limit
    assert 429 in responses


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
