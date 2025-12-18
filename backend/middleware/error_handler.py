"""
Global Error Handler Middleware
Centralized error handling and logging
"""

import traceback
import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Global error handler middleware"""
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        
        except ValidationError as e:
            logger.error(f"Validation error: {e}", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "error": "Validation Error",
                    "detail": e.errors(),
                    "request_id": getattr(request.state, 'request_id', 'unknown')
                }
            )
        
        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Database Error",
                    "message": "An error occurred while accessing the database",
                    "request_id": getattr(request.state, 'request_id', 'unknown')
                }
            )
        
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Internal Server Error",
                    "message": str(e) if not isinstance(e, Exception) else "An unexpected error occurred",
                    "request_id": getattr(request.state, 'request_id', 'unknown'),
                    "type": type(e).__name__
                }
            )


async def http_exception_handler(request: Request, exc: Exception):
    """Custom exception handler for HTTPException"""
    logger.warning(f"HTTP exception: {exc}")
    
    return JSONResponse(
        status_code=getattr(exc, 'status_code', 500),
        content={
            "error": getattr(exc, 'detail', str(exc)),
            "request_id": getattr(request.state, 'request_id', 'unknown')
        }
    )
