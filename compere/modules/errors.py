"""
Centralized error handling with safe error messages.
"""

import logging

from fastapi import HTTPException

from .config import is_development

logger = logging.getLogger(__name__)


def handle_database_error(e: Exception, operation: str = "operation") -> None:
    """Handle database errors with safe user-facing messages.

    Args:
        e: The exception that occurred
        operation: Description of the operation that failed

    Raises:
        HTTPException: Always raises with appropriate status code and message
    """
    # Always log the full error
    logger.error(f"Database error during {operation}: {str(e)}", exc_info=True)

    # In development, show details; in production, hide them
    if is_development():
        detail = f"Database error: {str(e)}"
    else:
        detail = "An internal error occurred. Please try again later."

    raise HTTPException(status_code=500, detail=detail) from e


def handle_not_found(resource: str, resource_id: int | str | None = None) -> None:
    """Handle resource not found errors.

    Args:
        resource: Name of the resource (e.g., "Entity", "Comparison")
        resource_id: Optional ID of the resource

    Raises:
        HTTPException: Always raises with 404 status code
    """
    if resource_id is not None:
        detail = f"{resource} with id {resource_id} not found"
    else:
        detail = f"{resource} not found"

    raise HTTPException(status_code=404, detail=detail)


def handle_validation_error(message: str) -> None:
    """Handle validation errors.

    Args:
        message: The validation error message

    Raises:
        HTTPException: Always raises with 400 status code
    """
    raise HTTPException(status_code=400, detail=message)


def handle_insufficient_data(message: str) -> None:
    """Handle errors when there's insufficient data for an operation.

    Args:
        message: Description of what's missing

    Raises:
        HTTPException: Always raises with 400 status code
    """
    raise HTTPException(status_code=400, detail=message)
