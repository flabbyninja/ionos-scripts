import requests

DEFAULT_TIMEOUT = 2


def get_rest_endpoint(url, headers, params, timeout=DEFAULT_TIMEOUT):
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
    response = requests.post(url, headers=headers,
                             json=payload, timeout=timeout)
    if response.status_code == 200 or response.status_code == 201:
        try:
            return response.json()
        except ValueError:
            return response.text
    else:
        return f"Error: {response.status_code} - {response.reason}"
