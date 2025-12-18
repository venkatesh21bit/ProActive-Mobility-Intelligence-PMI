"""
Request ID Middleware
Adds unique request ID to each request for tracing and logging
"""

import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from contextvars import ContextVar
import logging

# Context variable to store request ID
request_id_context: ContextVar[str] = ContextVar('request_id', default='')

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add unique request ID to each request"""
    
    async def dispatch(self, request: Request, call_next):
        # Generate or extract request ID
        request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())
        
        # Store in context variable
        request_id_context.set(request_id)
        
        # Add to request state
        request.state.request_id = request_id
        
        # Process request
        response = await call_next(request)
        
        # Add request ID to response headers
        response.headers['X-Request-ID'] = request_id
        
        return response


def get_request_id() -> str:
    """Get current request ID from context"""
    return request_id_context.get()


class RequestIDFilter(logging.Filter):
    """Logging filter to add request ID to log records"""
    
    def filter(self, record):
        record.request_id = request_id_context.get() or 'no-request-id'
        return True
