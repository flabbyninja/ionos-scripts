import os
import logging
import requests
from dotenv import load_dotenv

TARGET_DOMAIN = "example.com"
DEFAULT_TIMEOUT = 5
DYNDNS_URL = "https://api.hosting.ionos.com/dns/v1/dyndns"

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S'
)


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
    payload = {
        "domains": [
            f"{domain}"
        ],
        "description": "My DynamicDns"
    }

    result = post_to_rest_endpoint(DYNDNS_URL, headers, payload)
    return result


def main():
    load_dotenv()
    api_key = os.getenv("API_KEY")
    target_domain = os.getenv("DOMAIN")

    if (target_domain is None) or (len(target_domain) == 0):
        raise ValueError("Target zone not specified", target_domain)

    logging.info("Loading API key and target domain from environment")
    headers = {
        'X-API-Key': api_key,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    logging.info(
        "Calling IONOS API to update source IP for domain %s", target_domain)
    result = update_dynamic_dns(headers, target_domain)
    logging.debug("API result: %s", result)
    logging.info("Dynamic DNS update complete")


main()
