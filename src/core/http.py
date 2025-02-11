import aiohttp
import os
from typing import Any, Optional, Tuple
import json

class HTTPClient:
    """Generic HTTP client for making API requests"""
    
    def __init__(self, base_url: str = "", headers: Optional[dict] = None):
        """Initialize the HTTP client
        
        Args:
            base_url: Base URL for all requests
            headers: Default headers to include with all requests
        """
        self.base_url = base_url
        self.headers = headers or {}
        self._init_session()

    def _init_session(self) -> None:
        """Initialize the aiohttp client session. Can be overridden by subclasses."""
        self.session = aiohttp.ClientSession(base_url=self.base_url, headers=self.headers)

    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        expected_type: str = "application/json",
        **kwargs
    ) -> Tuple[int, Any]:
        """Make HTTP request and return status code and response
        
        Args:
            method: HTTP method to use
            endpoint: URL endpoint to request
            expected_type: Expected content type of response
            **kwargs: Additional arguments passed to the request
        """
        async with getattr(self.session, method)(endpoint, **kwargs) as resp:
            status = resp.status
            
            # For 204 No Content, just return status
            if status == 204:
                return status, None
                
            # For JSON responses
            if "application/json" in expected_type:
                try:
                    return status, await resp.json()
                except:
                    return status, None
                    
            # For text responses
            if "text" in expected_type:
                return status, await resp.text()
                
            # Default to returning raw response
            return status, await resp.read()

    async def get(self, endpoint: str, **kwargs) -> Tuple[int, Any]:
        """Make GET request"""
        return await self._make_request('get', endpoint, **kwargs)

    async def post(self, endpoint: str, **kwargs) -> Tuple[int, Any]:
        """Make POST request"""
        return await self._make_request('post', endpoint, **kwargs)

    async def put(self, endpoint: str, **kwargs) -> Tuple[int, Any]:
        """Make PUT request"""
        return await self._make_request('put', endpoint, **kwargs)

    async def delete(self, endpoint: str, **kwargs) -> Tuple[int, Any]:
        """Make DELETE request"""
        return await self._make_request('delete', endpoint, **kwargs)

    async def patch(self, endpoint: str, **kwargs) -> Tuple[int, Any]:
        """Make PATCH request"""
        return await self._make_request('patch', endpoint, **kwargs)

    async def close(self):
        """Close the client session"""
        if hasattr(self, 'session'):
            await self.session.close()
