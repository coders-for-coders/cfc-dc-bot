from nacl.signing import VerifyKey
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
import os

CLIENT_PUBLIC_KEY = os.environ.get("CLIENT_PUBLIC_KEY")


def verify_key(
    raw_body: bytes, signature: str, timestamp: str, client_public_key: str
) -> bool:
    """Verify the signature of the request
    
    Args:
        raw_body: The raw body of the request
        signature: The signature of the request
        timestamp: The timestamp of the request
        client_public_key: The public key of the client
        
    Returns:
        True if the signature is valid, False otherwise
    """
    message = timestamp.encode() + raw_body
    try:
        vk = VerifyKey(bytes.fromhex(client_public_key))
        vk.verify(message, bytes.fromhex(signature))
        return True
    except Exception as ex:
        print(ex)
    return False


async def set_body(request: Request, body: bytes):
    """Set the body of the request
    
    Args:
        request: The request object
        body: The body of the request
    """
    async def receive():
        return {"type": "http.request", "body": body}

    request._receive = receive


async def get_body(request: Request) -> bytes:
    """Get the body of the request
    
    Args:
        request: The request object
        
    Returns:
        The body of the request
    """
    body = await request.body()
    await set_body(request, body)
    return body


class CustomHeaderMiddleware(BaseHTTPMiddleware):
    """Middleware to verify the request signature
    
    Args:
        request: The request object
        call_next: The next middleware in the chain
        
    Returns:
        The response from the next middleware
    """
    async def dispatch(self, request, call_next):
        # Skip verification for non-Discord endpoints
        if request.url.path != "/discord":
            return await call_next(request)
            
        signature = request.headers.get("X-Signature-Ed25519")
        timestamp = request.headers.get("X-Signature-Timestamp")
        request_body = await get_body(request)
        if (
            signature is None
            or timestamp is None
            or not verify_key(request_body, signature, timestamp, CLIENT_PUBLIC_KEY)
        ):
            return Response("Bad request signature", status_code=401)
        response = await call_next(request)
        return response
