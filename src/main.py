from contextlib import asynccontextmanager
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Request
from starlette.middleware import Middleware
import uvicorn
from dotenv import load_dotenv
import logging

from core.command_handler import CommandHandler
from core.loader import CommandLoader
from utils import (
    CustomHeaderMiddleware,
    InteractionResponseFlags,
    InteractionResponseType,
    InteractionType,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Discord Bot",
    description="API for handling Discord bot interactions",
    middleware=[Middleware(CustomHeaderMiddleware)]
)

async def handle_interaction(interaction_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle different types of Discord interactions"""
    
    # Handle ping/pong for Discord's health check
    if interaction_data["type"] == InteractionType.PING:
        return {"type": InteractionResponseType.PONG}
    
    # Handle slash commands
    if interaction_data["type"] == InteractionType.APPLICATION_COMMAND:
        handler = CommandHandler(interaction_data)
        result = await handler.execute()
        
        if result is not None:
            return result
            
        return {
            "type": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
            "data": {
                "content": "Command not found or failed to execute.",
                "flags": InteractionResponseFlags.EPHEMERAL,
            },
        }
    
    # Default response for unhandled interaction types        
    return {
        "type": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
        "data": {
            "content": "Unsupported interaction type.",
            "flags": InteractionResponseFlags.EPHEMERAL,
        },
    }

@app.post("/discord")
async def interactions(request: Request) -> Dict[str, Any]:
    """Main endpoint for handling Discord interactions"""
    try:
        interaction_data = await request.json()
        return await handle_interaction(interaction_data)
    except Exception as e:
        logger.error(f"Error handling interaction: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
        
@app.get("/")
async def root():
    return {"message": "Hello World"}


async def startup_event():
    """Load commands when the application starts"""
    await CommandLoader.load_commands()

app.add_event_handler("startup", startup_event)

if __name__ == "__main__":
    load_dotenv()
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=3000,
        log_level="info"
    )
