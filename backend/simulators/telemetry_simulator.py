"""
Vehicle Telemetry Simulator
Generates realistic sensor data for 10 vehicles and exposes via WebSocket and HTTP endpoints
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

import asyncio
import random
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class VehicleTelemetry:
    """Vehicle telemetry data structure"""
    timestamp: str
    vehicle_id: str
    vin: str
    engine_temperature: float  # Celsius
    coolant_temperature: float  # Celsius
    oil_pressure: float  # PSI
    vibration_level: float  # G-force
    rpm: int
    speed: float  # km/h
    fuel_level: float  # percentage
    battery_voltage: float  # volts
    odometer: int  # km
    latitude: float
    longitude: float


class VehicleState:
    """Maintains state for a single vehicle"""
    
    def __init__(self, vehicle_id: int, vin: str):
        self.vehicle_id = f"VEH_{vehicle_id:03d}"
        self.vin = vin
        self.odometer = random.randint(5000, 150000)
        self.fuel_level = random.uniform(20, 95)
        self.latitude = 39.7817 + random.uniform(-0.1, 0.1)  # Springfield, IL area
        self.longitude = -89.6501 + random.uniform(-0.1, 0.1)
        
        # Failure simulation flags
        self.has_engine_issue = random.random() < 0.1  # 10% chance of engine issue
        self.has_oil_issue = random.random() < 0.05  # 5% chance of oil issue
        self.has_vibration_issue = random.random() < 0.08  # 8% chance of vibration issue
        
    def generate_telemetry(self) -> VehicleTelemetry:
        """Generate realistic telemetry data with potential anomalies"""
        
        # Normal operating ranges
        base_engine_temp = 90.0
        base_coolant_temp = 85.0
        base_oil_pressure = 45.0
        base_vibration = 0.5
        
        # Inject anomalies if vehicle has issues
        if self.has_engine_issue:
            engine_temp = random.uniform(105, 125)  # Overheating
            coolant_temp = random.uniform(95, 110)
        else:
            engine_temp = random.gauss(base_engine_temp, 5)
            coolant_temp = random.gauss(base_coolant_temp, 3)
        
        if self.has_oil_issue:
            oil_pressure = random.uniform(15, 30)  # Low oil pressure
        else:
            oil_pressure = random.gauss(base_oil_pressure, 5)
        
        if self.has_vibration_issue:
            vibration = random.uniform(2.0, 4.5)  # High vibration
        else:
            vibration = random.gauss(base_vibration, 0.2)
        
        # Normal parameters with some variance
        rpm = random.randint(800, 3500)
        speed = random.uniform(0, 120)
        battery_voltage = random.gauss(12.6, 0.3)
        
        # Update fuel and odometer
        self.fuel_level = max(0, self.fuel_level - random.uniform(0, 0.5))
        if self.fuel_level < 5:
            self.fuel_level = random.uniform(80, 95)  # Refuel
        
        self.odometer += random.randint(0, 2)
        
        # Small GPS drift
        self.latitude += random.uniform(-0.001, 0.001)
        self.longitude += random.uniform(-0.001, 0.001)
        
        return VehicleTelemetry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            vehicle_id=self.vehicle_id,
            vin=self.vin,
            engine_temperature=round(engine_temp, 2),
            coolant_temperature=round(coolant_temp, 2),
            oil_pressure=round(oil_pressure, 2),
            vibration_level=round(vibration, 3),
            rpm=rpm,
            speed=round(speed, 2),
            fuel_level=round(self.fuel_level, 2),
            battery_voltage=round(battery_voltage, 2),
            odometer=self.odometer,
            latitude=round(self.latitude, 6),
            longitude=round(self.longitude, 6)
        )


class TelemetrySimulator:
    """Manages multiple vehicles and generates telemetry"""
    
    def __init__(self, num_vehicles: int = 10):
        self.vehicles: List[VehicleState] = []
        self.active_websockets: List[WebSocket] = []
        self._initialize_vehicles(num_vehicles)
        
    def _initialize_vehicles(self, num_vehicles: int):
        """Initialize vehicle fleet"""
        makes_models = [
            ("Toyota", "Camry"), ("Honda", "Accord"), ("Ford", "F-150"),
            ("Chevrolet", "Silverado"), ("Tesla", "Model 3"),
            ("BMW", "X5"), ("Mercedes", "C-Class"), ("Audi", "A4"),
            ("Nissan", "Altima"), ("Hyundai", "Elantra")
        ]
        
        for i in range(num_vehicles):
            vin = f"1HGBH41JXMN{i:06d}"
            self.vehicles.append(VehicleState(i + 1, vin))
        
        logger.info(f"Initialized {num_vehicles} vehicles")
    
    def get_all_telemetry(self) -> List[Dict]:
        """Get current telemetry for all vehicles"""
        return [asdict(vehicle.generate_telemetry()) for vehicle in self.vehicles]
    
    def get_vehicle_telemetry(self, vehicle_id: str) -> Optional[Dict]:
        """Get telemetry for specific vehicle"""
        for vehicle in self.vehicles:
            if vehicle.vehicle_id == vehicle_id:
                return asdict(vehicle.generate_telemetry())
        return None
    
    async def broadcast_telemetry(self):
        """Continuously broadcast telemetry to all connected WebSocket clients"""
        while True:
            if self.active_websockets:
                telemetry_batch = self.get_all_telemetry()
                
                disconnected = []
                for websocket in self.active_websockets:
                    try:
                        await websocket.send_json(telemetry_batch)
                    except Exception as e:
                        logger.error(f"Error sending to WebSocket: {e}")
                        disconnected.append(websocket)
                
                # Remove disconnected clients
                for ws in disconnected:
                    self.active_websockets.remove(ws)
            
            await asyncio.sleep(5)  # Send every 5 seconds


# FastAPI Application
app = FastAPI(
    title="Vehicle Telemetry Simulator",
    description="Simulates telemetry data for 10 vehicles",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize simulator
simulator = TelemetrySimulator(num_vehicles=10)


@app.on_event("startup")
async def startup_event():
    """Start background telemetry broadcast"""
    asyncio.create_task(simulator.broadcast_telemetry())
    logger.info("Telemetry simulator started")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Vehicle Telemetry Simulator",
        "version": "1.0.0",
        "vehicles": len(simulator.vehicles),
        "endpoints": {
            "all_telemetry": "/telemetry",
            "vehicle_telemetry": "/telemetry/{vehicle_id}",
            "websocket": "/ws"
        }
    }


@app.get("/telemetry")
async def get_all_telemetry():
    """Get current telemetry for all vehicles via HTTP"""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "count": len(simulator.vehicles),
        "telemetry": simulator.get_all_telemetry()
    }


@app.get("/telemetry/{vehicle_id}")
async def get_vehicle_telemetry(vehicle_id: str):
    """Get telemetry for specific vehicle via HTTP"""
    telemetry = simulator.get_vehicle_telemetry(vehicle_id)
    if telemetry:
        return telemetry
    return {"error": "Vehicle not found"}, 404


@app.get("/vehicles")
async def list_vehicles():
    """List all vehicle IDs"""
    return {
        "count": len(simulator.vehicles),
        "vehicles": [
            {
                "vehicle_id": v.vehicle_id,
                "vin": v.vin,
                "has_engine_issue": v.has_engine_issue,
                "has_oil_issue": v.has_oil_issue,
                "has_vibration_issue": v.has_vibration_issue
            }
            for v in simulator.vehicles
        ]
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time telemetry streaming"""
    await websocket.accept()
    simulator.active_websockets.append(websocket)
    logger.info(f"WebSocket client connected. Total clients: {len(simulator.active_websockets)}")
    
    try:
        while True:
            # Keep connection alive and handle client messages if needed
            data = await websocket.receive_text()
            logger.debug(f"Received from client: {data}")
    except WebSocketDisconnect:
        simulator.active_websockets.remove(websocket)
        logger.info(f"WebSocket client disconnected. Total clients: {len(simulator.active_websockets)}")


if __name__ == "__main__":
    uvicorn.run(
        "telemetry_simulator:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
