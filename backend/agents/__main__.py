"""
Main entry point for Master Agent with Ray
Run this to start the autonomous service orchestration system
"""

import sys
from pathlib import Path
import logging
import asyncio

# Add parent directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

import ray
from agents.master_agent import MasterAgent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Initialize Ray and start Master Agent"""
    
    logger.info("Starting Master Agent System...")
    
    # Initialize Ray
    logger.info("Initializing Ray...")
    try:
        ray.init(
            ignore_reinit_error=True,
            logging_level=logging.INFO,
            num_cpus=4  # Adjust based on your system
        )
        logger.info("Ray initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Ray: {e}")
        return
    
    try:
        # Create Master Agent actor
        logger.info("Creating Master Agent actor...")
        master_agent = MasterAgent.remote()
        
        # Initialize agent (connect to Redis, etc.)
        logger.info("Initializing Master Agent...")
        ray.get(master_agent.initialize.remote())
        
        logger.info("=" * 60)
        logger.info("Master Agent is now running!")
        logger.info("=" * 60)
        logger.info("Listening for alerts on Redis stream: alerts:predicted")
        logger.info("Press Ctrl+C to stop")
        logger.info("=" * 60)
        
        # Start listening for alerts (blocking)
        ray.get(master_agent.start_listening.remote())
        
    except KeyboardInterrupt:
        logger.info("\nShutting down Master Agent...")
    except Exception as e:
        logger.error(f"Error running Master Agent: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ray.shutdown()
        logger.info("Master Agent stopped")


if __name__ == "__main__":
    main()
