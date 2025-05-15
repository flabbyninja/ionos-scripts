import os
import requests
from dotenv import load_dotenv

TARGET_DOMAIN = "example.com"
DEFAULT_TIMEOUT = 5


def post_to_rest_endpoint(url, headers, payload):
    response = requests.post(url, headers=headers,
                             json=payload, timeout=DEFAULT_TIMEOUT)
    if response.status_code == 200 or response.status_code == 201:
        try:
            return response.json()
        except ValueError:
            return response.text
    else:
        return f"Error: {response.status_code} - {response.reason}"


def update_dynamic_dns(headers, domain):
    url = 'https://api.hosting.ionos.com/dns/v1/dyndns'
    payload = {
        "domains": [
            f"{domain}"
        ],
        "description": "My DynamicDns"
    }

    result = post_to_rest_endpoint(url, headers, payload)
    return result


def main():
    load_dotenv()
    api_key = os.getenv("API_KEY")
    target_domain = os.getenv("DOMAIN")

    if (target_domain is None) or (len(target_domain) == 0):
        raise ValueError("Target zone not specified", target_domain)

    headers = {
        'X-API-Key': api_key,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    result = update_dynamic_dns(headers, target_domain)
    print(result)


main()
