"""
Response formatting utilities for dashboard API
"""
from typing import Any, Dict, Optional
from flask import jsonify


def success_response(data: Any = None, message: str = "Success") -> Dict:
    """
    Create a standardized success response

    Args:
        data: Response data (can be dict, list, or any JSON-serializable type)
        message: Success message

    Returns:
        Formatted response dictionary
    """
    response = {
        "success": True,
        "message": message
    }
    if data is not None:
        response["data"] = data
    return jsonify(response)


def error_response(error: str, status_code: int = 400, details: Optional[Dict] = None) -> tuple:
    """
    Create a standardized error response

    Args:
        error: Error message
        status_code: HTTP status code
        details: Additional error details

    Returns:
        Tuple of (response dict, status code)
    """
    response = {
        "success": False,
        "error": error
    }
    if details:
        response["details"] = details
    return jsonify(response), status_code


def format_number(value: Any, default: int = 0) -> int:
    """
    Format a number value by removing commas and converting to int

    Args:
        value: Value to format (can be string with commas, int, or float)
        default: Default value if conversion fails

    Returns:
        Formatted integer value
    """
    try:
        if value is None:
            return default
        if isinstance(value, str):
            return int(value.replace(',', ''))
        return int(value)
    except (ValueError, AttributeError):
        return default


def format_currency(amount: int) -> str:
    """
    Format an integer amount as currency with comma separators

    Args:
        amount: Amount to format

    Returns:
        Formatted currency string (e.g., "1,234,567")
    """
    return f"{amount:,}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format a decimal value as percentage

    Args:
        value: Value to format (e.g., 0.1523 for 15.23%)
        decimals: Number of decimal places

    Returns:
        Formatted percentage string (e.g., "15.23%")
    """
    return f"{value * 100:.{decimals}f}%"
