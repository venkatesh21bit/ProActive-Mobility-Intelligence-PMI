"""
Telemetry Stream Consumer
Consumes telemetry data from Redis Streams and performs real-time processing
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

import asyncio
import json
import logging
from typing import Dict, List
from datetime import datetime

from data.redis_client import redis_stream_client
from config.settings import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TelemetryConsumer:
    """
    Consumes telemetry data from Redis Streams for real-time processing
    """
    
    def __init__(self, group_name: str = "telemetry-processors", consumer_name: str = "consumer-1"):
        self.group_name = group_name
        self.consumer_name = consumer_name
        self.running = False
        
    async def process_telemetry(self, message_id: str, data: Dict) -> bool:
        """
        Process a single telemetry message
        
        Args:
            message_id: Redis Stream message ID
            data: Telemetry data
            
        Returns:
            True if processing successful, False otherwise
        """
        try:
            # Parse data
            vehicle_id = data.get('vehicle_id', 'unknown')
            vin = data.get('vin', 'unknown')
            
            # Extract sensor values
            engine_temp = float(data.get('engine_temperature', 0))
            oil_pressure = float(data.get('oil_pressure', 0))
            vibration = float(data.get('vibration_level', 0))
            
            # Check for anomalies (simple threshold-based for now)
            anomalies = []
            
            if engine_temp > 105:
                anomalies.append(f"High engine temperature: {engine_temp}°C")
            
            if oil_pressure < 25:
                anomalies.append(f"Low oil pressure: {oil_pressure} PSI")
            
            if vibration > 2.0:
                anomalies.append(f"High vibration level: {vibration}g")
            
            if anomalies:
                logger.warning(f"[{vehicle_id}] Anomalies detected: {', '.join(anomalies)}")
                
                # Publish alert to alerts stream
                alert_data = {
                    "vehicle_id": vehicle_id,
                    "vin": vin,
                    "timestamp": datetime.utcnow().isoformat(),
                    "anomalies": anomalies,
                    "severity": "high" if len(anomalies) > 1 else "medium",
                    "sensor_data": {
                        "engine_temperature": engine_temp,
                        "oil_pressure": oil_pressure,
                        "vibration_level": vibration
                    }
                }
                
                await redis_stream_client.add_to_stream(
                    alert_data,
                    stream_name=settings.alerts_stream_name
                )
                logger.info(f"[{vehicle_id}] Alert published to {settings.alerts_stream_name}")
            else:
                logger.debug(f"[{vehicle_id}] Telemetry processed successfully - no anomalies")
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing telemetry {message_id}: {e}")
            return False
    
    async def consume_stream(self):
        """
        Main consumer loop - continuously read and process messages
        """
        logger.info(f"Starting consumer '{self.consumer_name}' in group '{self.group_name}'")
        
        self.running = True
        consecutive_errors = 0
        
        while self.running:
            try:
                # Read messages from stream (blocking for 5 seconds)
                messages = await redis_stream_client.read_group(
                    group_name=self.group_name,
                    consumer_name=self.consumer_name,
                    stream_name=settings.redis_stream_name,
                    count=10,
                    block=5000
                )
                
                if not messages:
                    # No new messages
                    await asyncio.sleep(0.1)
                    continue
                
                # Process each message
                for message_id, data in messages:
                    success = await self.process_telemetry(message_id, data)
                    
                    if success:
                        # Acknowledge successful processing
                        await redis_stream_client.acknowledge(
                            group_name=self.group_name,
                            message_id=message_id,
                            stream_name=settings.redis_stream_name
                        )
                        consecutive_errors = 0
                    else:
                        consecutive_errors += 1
                        logger.warning(f"Failed to process message {message_id}")
                
                # Safety check - if too many errors, pause
                if consecutive_errors > 10:
                    logger.error("Too many consecutive errors, pausing for 30 seconds")
                    await asyncio.sleep(30)
                    consecutive_errors = 0
                    
            except asyncio.CancelledError:
                logger.info("Consumer cancelled")
                break
            except Exception as e:
                logger.error(f"Error in consumer loop: {e}")
                consecutive_errors += 1
                await asyncio.sleep(5)
    
    def stop(self):
        """Stop the consumer"""
        logger.info(f"Stopping consumer '{self.consumer_name}'")
        self.running = False


async def main():
    """Main entry point for consumer service"""
    logger.info("Initializing Telemetry Consumer Service")
    
    # Connect to Redis
    await redis_stream_client.connect()
    
    # Ensure consumer group exists
    try:
        await redis_stream_client.create_consumer_group(
            group_name="telemetry-processors",
            stream_name=settings.redis_stream_name,
            start_id="0"
        )
    except Exception as e:
        logger.warning(f"Consumer group setup: {e}")
    
    # Create and ensure alerts stream group exists
    try:
        await redis_stream_client.create_consumer_group(
            group_name="alert-handlers",
            stream_name=settings.alerts_stream_name,
            start_id="0"
        )
    except Exception as e:
        logger.warning(f"Alerts group setup: {e}")
    
    # Create consumer
    consumer = TelemetryConsumer(
        group_name="telemetry-processors",
        consumer_name=f"consumer-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    )
    
    try:
        # Run consumer
        await consumer.consume_stream()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    finally:
        consumer.stop()
        await redis_stream_client.disconnect()
        logger.info("Consumer service stopped")


if __name__ == "__main__":
    asyncio.run(main())
