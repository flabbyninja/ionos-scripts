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
    response = requests.get(url, headers=headers,
                            params=params, timeout=timeout)
    if response.status_code == 200:
        # print(response.url)
        # print(response.text)
        try:
            data = response.json()  # Process JSON response
            return data
        except ValueError:
            return response.text  # Return raw text if not JSON
    else:
        return f"Error: {response.status_code} - {response.reason}"


def post_to_rest_endpoint(url, headers, payload, timeout=DEFAULT_TIMEOUT):
    """
    Utility method to support POST method calls to RESTful endpoint. Supports custom
    headers, addition of payload and configurable timeout.
    """
    response = requests.post(url, headers=headers,
                             json=payload, timeout=timeout)
    if response.status_code == 200 or response.status_code == 201:
        try:
            return response.json()
        except ValueError:
            return response.text
    else:
        return f"Error: {response.status_code} - {response.reason}"
