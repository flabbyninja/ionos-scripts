"""
Uses the IONOS Developer DNS API to update DynamicDNS config of
a domain name to match the public IP of where the call was made from.
This will get the current IP from DNS, and find the current public IP 
and only perform the update if they don't currently match. This prevents
unnecessary calls to the IONOS API.
"""
import os
import logging

from dotenv import load_dotenv

import rest_utils
import dns_utils

IONOS_TIMEOUT = 5

DYNDNS_URL = "https://api.hosting.ionos.com/dns/v1/dyndns"

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S'
)


def disable_dynamic_dns(headers):
    """
    Perform the IONOS API call to disable Dynamic DNS
    """
    result = rest_utils.delete_rest_endpoint(
        DYNDNS_URL, headers, IONOS_TIMEOUT)
    return result


def update_dynamic_dns(headers, domain):
    """
    Perform the IONOS API call to perform the Dynamic DNS update
    """
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
    """
    Load API key for IONOS API and config for domain from .env
    Checks whether the public IP already matches what DNS is set to.
    If there is a mismatch, make the call to IONOS to update
    DynamicDNS config
    """
    load_dotenv()
    api_key = os.getenv("API_KEY")
    target_domain = os.getenv("DOMAIN")
    delete_first = os.getenv("DELETE_FIRST")

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

        if delete_first == '1':
            logging.info("Config: Disabling Dynamic DNS before updating")
            disable_response = disable_dynamic_dns(headers)
            logging.info(disable_response)

        logging.info(
            "Calling IONOS API to update source IP for domain %s", target_domain)
        result = update_dynamic_dns(headers, target_domain)
        logging.debug("API result: %s", result)
        logging.info("Dynamic DNS result received complete")
        dyn_update_url = result["updateUrl"]
        logging.info("Update URL from response is %s", dyn_update_url)
        result = rest_utils.get_rest_endpoint(dyn_update_url)
        print(result)
    else:
        logging.info("No Dynamic DNS update required.")


main()
