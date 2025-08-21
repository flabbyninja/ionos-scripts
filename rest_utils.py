"""
Utility methods to support making RESTful calls to endpoints
"""
import requests

DEFAULT_TIMEOUT = 2


def get_rest_endpoint(url, headers=None, params=None, timeout=DEFAULT_TIMEOUT):
    """
    Utility method to support GET method calls to RESTful endpoint. Supports custom
    headers, passing params and configurable timeout.
    """
    response = generic_request("GET", url, headers=headers, timeout=timeout)

    return response


def post_to_rest_endpoint(url, headers, payload, timeout=DEFAULT_TIMEOUT):
    """
    Utility method to support POST method calls to RESTful endpoint. Supports custom
    headers, addition of payload and configurable timeout.
    """

    response = generic_request(
        "POST", url, headers, timeout=timeout, data=payload)

    return response


def delete_rest_endpoint(url, headers, timeout=DEFAULT_TIMEOUT):
    """
    Utility method to support DELETE method calls to RESTful endpoint. Supports custom header, and
    configurable timeout
    """
    result = generic_request("DELETE", url, headers, timeout)

    return result


def generic_request(method, url, headers=None, timeout=DEFAULT_TIMEOUT, data=None, params=None):
    """
    Utility method for making GET, POST, and DELETE requests to RESTful API endpoints.

    Args:
        method (str): The HTTP method ("GET", "POST", "DELETE").
        url (str): The endpoint URL.
        headers (dict, optional): Request headers. Defaults to None.
        timeout (int, optional): Timeout in seconds. Defaults to 10.
        data (dict, optional): Data for POST requests. Defaults to None.
        params (dict, optional): Query parameters for GET requests. Defaults to None.

    Returns:
        dict: A response dictionary with keys:
              - "success": bool (True if request was successful)
              - "status_code": int (HTTP status code)
              - "data": dict or str (JSON payload if available, otherwise text)
              - "error": str (error message if request failed)
    """
    try:
        # Normalize method
        method = method.upper()
        if method not in ["GET", "POST", "DELETE"]:
            raise ValueError(f"Unsupported method: {method}")

        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            timeout=timeout,
            json=data if method == "POST" else None,
            params=params
        )

        # Try parsing as JSON
        try:
            payload = response.json()
        except ValueError:
            payload = response.text

        return {
            "success": response.ok,
            "status_code": response.status_code,
            "data": payload,
            "error": None if response.ok else f"HTTP {response.status_code}"
        }

    except requests.exceptions.RequestException as e:
        # Catch request-related errors (timeouts, connection errors, etc.)
        return {
            "success": False,
            "status_code": None,
            "data": None,
            "error": str(e)
        }
