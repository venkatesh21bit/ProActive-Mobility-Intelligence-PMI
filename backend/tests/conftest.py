"""Test configuration and fixtures"""

import pytest


@pytest.fixture(scope="session")
def test_config():
    """Test configuration"""
    return {
        "database_url": "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db",
        "redis_host": "localhost",
        "redis_port": 6379,
        "jwt_secret": "test_secret_key_for_testing_only"
    }
