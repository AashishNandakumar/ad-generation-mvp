from fastapi import Header, HTTPException
from typing import Optional
from ..config import settings


async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Verify API key in request header."""
    if not x_api_key or x_api_key != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return x_api_key


async def get_trend_agent():
    """Dependency to get TrendAgent instance."""
    from ..core.agents.trend_agent import TrendAgent

    return TrendAgent()


async def get_image_agent():
    """Dependency to get ImageAgent instance."""
    from ..core.agents.image_agent import ImageAgent

    return ImageAgent()


async def get_file_processor():
    """Dependency to get FileProcessor instance."""
    from ..core.utils.file_processor import FileProcessor

    return FileProcessor()
