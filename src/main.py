# src/main.py
"""
Main entry point for Food Delivery Platform
"""

import asyncio
import logging
from live_app import app
from .food_delivery_platform import FoodDeliveryPlatform

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Main application entry point"""
    try:
        logger.info("Starting Food Delivery Platform...")
        
        # Initialize platform
        platform = FoodDeliveryPlatform()
        
        # Keep the application running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Shutting down Food Delivery Platform...")
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
