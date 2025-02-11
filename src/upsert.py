from dotenv import load_dotenv
import os
import asyncio
import logging
from core.http import HTTPClient
from core.loader import CommandLoader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

TOKEN = os.environ.get("DISCORD_TOKEN")
APPLICATION_ID = os.environ.get("APPLICATION_ID")

async def update_commands():
    """Update Discord application commands"""
    # Load all commands first
    await CommandLoader.load_commands()
    
    from core import registry
    
    discord_client = HTTPClient(
        base_url="https://discord.com/api/v10/",
        headers={"Authorization": f"Bot {TOKEN}"}
    )
    
    try:
        commands = registry.all_commands()
        logger.info(f"Commands to update: {[c.name for c in commands]}")
        
        status, response = await discord_client.put(
            f"applications/{APPLICATION_ID}/commands",
            json=[c.to_dict() for c in commands]
        )
        
        if status == 200:
            logger.info("Successfully updated commands:")
            logger.info(response)
        else:
            logger.error(f"Error updating commands. Status: {status}")
            logger.error(response)
            
    except Exception as e:
        logger.error(f"Error updating commands: {e}", exc_info=True)
    finally:
        await discord_client.close()

if __name__ == "__main__":
    asyncio.run(update_commands())
