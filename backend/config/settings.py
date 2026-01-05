from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pathlib import Path

# Get the backend directory (parent of config directory)
BACKEND_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"
    )
    
    # Application
    app_name: str = "ProActive Mobility Intelligence"
    app_version: str = "1.0.0"
    environment: str = "development"
    api_port: int = 8000
    simulator_port: int = 8001
    
    # Database
    postgres_user: str = "pmi_user"
    postgres_password: str = "pmi_password"
    postgres_db: str = "pmi_db"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    database_url: str = "postgresql+asyncpg://pmi_user:pmi_password@localhost:5432/pmi_db"
    
    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = "redis_password"
    redis_url: str = "redis://:redis_password@localhost:6379/0"
    
    # MinIO
    minio_root_user: str = "minioadmin"
    minio_root_password: str = "minioadmin123"
    minio_port: int = 9000
    minio_console_port: int = 9001
    minio_endpoint: str = "localhost:9000"
    
    # MLflow
    mlflow_tracking_uri: str = "http://localhost:5000"
    mlflow_port: int = 5000
    
    # Monitoring
    prometheus_port: int = 9090
    grafana_port: int = 3000
    grafana_user: str = "admin"
    grafana_password: str = "admin123"
    
    # Security
    secret_key: str = "your-secret-key-change-this-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Twilio
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_phone_number: Optional[str] = None
    
    # Ray
    ray_address: str = "auto"
    ray_dashboard_port: int = 8265
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Telemetry Simulator
    num_vehicles: int = 10
    telemetry_interval_seconds: int = 5
    failure_probability: float = 0.05
    
    # Agent Configuration
    master_agent_host: str = "localhost"
    master_agent_port: int = 8080
    
    # Service Center
    service_center_api_url: str = "http://localhost:8002"
    
    def model_post_init(self, __context) -> None:
        """Post-initialization to fix database URL for asyncpg"""
        # Railway and other platforms provide postgresql:// but we need postgresql+asyncpg://
        if self.database_url.startswith("postgresql://"):
            self.database_url = self.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    @property
    def redis_stream_name(self) -> str:
        return "vehicle:telemetry"
    
    @property
    def alerts_stream_name(self) -> str:
        return "alerts:predicted"


# Global settings instance
settings = Settings()
