import os
import logging
from dotenv import load_dotenv

import rest_utils
import dns_utils

IONOS_TIMEOUT = 5

TARGET_DOMAIN = "example.com"
DYNDNS_URL = "https://api.hosting.ionos.com/dns/v1/dyndns"

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S'
)


def update_dynamic_dns(headers, domain):
    payload = {
        "domains": [
            f"{domain}"
        ],
        "description": "My DynamicDns"
    }

    result = rest_utils.post_to_rest_endpoint(
        DYNDNS_URL, headers, payload, IONOS_TIMEOUT)
    return result


def main():
    load_dotenv()
    api_key = os.getenv("API_KEY")
    target_domain = os.getenv("DOMAIN")

    if (target_domain is None) or (len(target_domain) == 0):
        raise ValueError("Target zone not specified", target_domain)

    if dns_utils.is_public_ip_up_to_date(target_domain) is False:
        logging.info("Public IP and DNS do not match - performing update")

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
    else:
        logging.info("No Dynamic DNS update required.")


main()
