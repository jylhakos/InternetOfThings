"""
Demonstration: Why @asynccontextmanager is essential for FastAPI Lifespan Management

This script shows the difference between proper and improper resource management
in FastAPI applications.
"""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simulated database connection
class DatabaseConnection:
    def __init__(self, name):
        self.name = name
        self.connected = False
        self.connection_count = 0
    
    async def connect(self):
        await asyncio.sleep(0.5)  # Simulate connection time
        self.connected = True
        self.connection_count += 1
        logger.info(f"✅ {self.name} - Database connected (attempt #{self.connection_count})")
    
    async def disconnect(self):
        await asyncio.sleep(0.3)  # Simulate disconnection time
        if self.connected:
            self.connected = False
            logger.info(f"❌ {self.name} - Database disconnected")
        else:
            logger.warning(f"⚠️  {self.name} - Attempted to disconnect already closed connection")
    
    def __del__(self):
        if self.connected:
            logger.error(f"🚨 {self.name} - Connection not properly closed! Memory leak detected!")

# Global database instances
db_proper = DatabaseConnection("PROPER")
db_improper = DatabaseConnection("IMPROPER")

# ==========================================
# PROPER WAY: Using @asynccontextmanager
# ==========================================

@asynccontextmanager
async def proper_lifespan(app: FastAPI):
    """
    Proper lifespan management using @asynccontextmanager
    Guarantees resource cleanup even if exceptions occur
    """
    logger.info("🚀 PROPER: Starting application...")
    
    try:
        # Startup operations
        await db_proper.connect()
        logger.info("✅ PROPER: Startup completed successfully")
        
        yield  # Application runs here
        
    except Exception as e:
        logger.error(f"🚨 PROPER: Error during lifespan: {e}")
        raise
    finally:
        # Shutdown operations (ALWAYS executed)
        logger.info("🛑 PROPER: Shutting down...")
        await db_proper.disconnect()
        logger.info("✅ PROPER: Shutdown completed successfully")

app_proper = FastAPI(
    title="Proper Lifespan Management",
    lifespan=proper_lifespan
)

@app_proper.get("/")
async def proper_root():
    return {
        "message": "Proper lifespan management",
        "database_connected": db_proper.connected
    }

# ==========================================
# IMPROPER WAY: Using deprecated events
# ==========================================

app_improper = FastAPI(title="Improper Lifespan Management")

@app_improper.on_event("startup")
async def improper_startup():
    """
    Deprecated startup event - no guaranteed cleanup
    """
    logger.info("🚀 IMPROPER: Starting application...")
    await db_improper.connect()
    logger.info("⚠️  IMPROPER: Startup completed (no guaranteed cleanup)")

@app_improper.on_event("shutdown")
async def improper_shutdown():
    """
    Deprecated shutdown event - may not execute in all scenarios
    """
    logger.info("🛑 IMPROPER: Attempting shutdown...")
    await db_improper.disconnect()
    logger.info("⚠️  IMPROPER: Shutdown completed (if it executed)")

@app_improper.get("/")
async def improper_root():
    return {
        "message": "Improper lifespan management",
        "database_connected": db_improper.connected
    }

# ==========================================
# Demonstration Functions
# ==========================================

async def demonstrate_proper_handling():
    """Demonstrate proper resource management"""
    print("\n" + "="*60)
    print("DEMONSTRATING PROPER LIFESPAN MANAGEMENT")
    print("="*60)
    
    @asynccontextmanager
    async def demo_lifespan():
        resource = DatabaseConnection("DEMO_PROPER")
        try:
            await resource.connect()
            logger.info("Resource acquired safely")
            yield resource
        except Exception as e:
            logger.error(f"Error in lifespan: {e}")
        finally:
            await resource.disconnect()
            logger.info("Resource cleaned up guaranteed")
    
    # Use the context manager
    async with demo_lifespan() as resource:
        logger.info(f"Using resource: connected={resource.connected}")
        # Simulate some work
        await asyncio.sleep(0.1)
    
    logger.info("✅ Proper demo completed - all resources cleaned up")

async def demonstrate_improper_handling():
    """Demonstrate improper resource management"""
    print("\n" + "="*60)
    print("DEMONSTRATING IMPROPER RESOURCE MANAGEMENT")
    print("="*60)
    
    resource = DatabaseConnection("DEMO_IMPROPER")
    await resource.connect()
    logger.info(f"Using resource: connected={resource.connected}")
    
    # Simulate forgetting to disconnect
    logger.warning("⚠️  Forgot to disconnect! Resource will leak...")
    # resource goes out of scope without proper cleanup

async def simulate_exception_scenario():
    """Demonstrate how @asynccontextmanager handles exceptions"""
    print("\n" + "="*60)
    print("DEMONSTRATING EXCEPTION HANDLING")
    print("="*60)
    
    @asynccontextmanager
    async def exception_lifespan():
        resource = DatabaseConnection("EXCEPTION_TEST")
        try:
            await resource.connect()
            logger.info("Resource connected before exception")
            yield resource
        except Exception as e:
            logger.error(f"Exception handled: {e}")
        finally:
            await resource.disconnect()
            logger.info("✅ Resource cleaned up despite exception")
    
    try:
        async with exception_lifespan() as resource:
            logger.info("About to raise an exception...")
            raise ValueError("Simulated error!")
    except ValueError as e:
        logger.info(f"Exception caught: {e}")

# ==========================================
# Main Demonstration
# ==========================================

async def main():
    """Run all demonstrations"""
    print("FastAPI Lifespan Management Demonstration")
    print("=" * 60)
    
    await demonstrate_proper_handling()
    await demonstrate_improper_handling()
    await simulate_exception_scenario()
    
    print("\n" + "="*60)
    print("KEY BENEFITS OF @asynccontextmanager:")
    print("="*60)
    print("1. ✅ Guaranteed resource cleanup")
    print("2. ✅ Exception safety")
    print("3. ✅ Proper async/await support")
    print("4. ✅ Context manager protocol")
    print("5. ✅ Future-proof (recommended by FastAPI)")
    print("6. ✅ Clear separation of startup/shutdown logic")
    print("\nDEPRECATED on_event() PROBLEMS:")
    print("1. ❌ No guaranteed cleanup")
    print("2. ❌ Poor exception handling")
    print("3. ❌ Separate startup/shutdown functions")
    print("4. ❌ May be removed in future FastAPI versions")

if __name__ == "__main__":
    # Run the demonstration
    asyncio.run(main())
    
    print("\n" + "="*60)
    print("To run the FastAPI applications:")
    print("="*60)
    print("# Proper lifespan management:")
    print("# uvicorn lifespan_demo:app_proper --reload --port 8001")
    print("#")
    print("# Improper lifespan management:")
    print("# uvicorn lifespan_demo:app_improper --reload --port 8002")
