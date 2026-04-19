"""Custom exceptions and FastAPI exception handlers.

Provides user-friendly error messages instead of raw Python tracebacks.
"""

from typing import Any, Optional

from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError


class DataDialogueError(Exception):
    """Base exception for all DataDialogue errors."""

    def __init__(
        self,
        message: str = "An unexpected error occurred",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Any] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


class NotFoundError(DataDialogueError):
    """Resource not found."""

    def __init__(self, resource: str = "Resource", resource_id: str = ""):
        super().__init__(
            message=f"{resource} not found" + (f": {resource_id}" if resource_id else ""),
            status_code=status.HTTP_404_NOT_FOUND,
        )


class AuthenticationError(DataDialogueError):
    """Authentication failed."""

    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class AuthorizationError(DataDialogueError):
    """User not authorized for this action."""

    def __init__(self, message: str = "Not authorized to perform this action"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class FileProcessingError(DataDialogueError):
    """Error during file processing."""

    def __init__(self, message: str = "Failed to process file", details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class QueryExecutionError(DataDialogueError):
    """Error during query execution."""

    def __init__(self, message: str = "Failed to execute query", details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class FileSizeExceededError(DataDialogueError):
    """Uploaded file exceeds maximum size."""

    def __init__(self, max_size_mb: int):
        super().__init__(
            message=f"File size exceeds maximum allowed size of {max_size_mb}MB",
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        )


class InvalidFileTypeError(DataDialogueError):
    """Uploaded file type not supported."""

    def __init__(self, file_type: str, allowed: list):
        super().__init__(
            message=f"File type '{file_type}' is not supported. Allowed: {', '.join(allowed)}",
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        )


async def datadialogue_error_handler(request: Request, exc: DataDialogueError) -> JSONResponse:
    """Handle DataDialogue custom exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "details": exc.details,
            "status_code": exc.status_code,
        },
    )


async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle Pydantic validation errors with user-friendly messages."""
    errors = []
    for error in exc.errors():
        field = " → ".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"],
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation error",
            "details": errors,
            "status_code": 422,
        },
    )


async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all unhandled exceptions with a safe message."""
    import traceback
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": f"An internal server error occurred: {str(exc)}",
            "details": traceback.format_exc(),
            "status_code": 500,
        },
    )
