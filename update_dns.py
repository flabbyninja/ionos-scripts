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

    if result["success"]:
        logging.info("Successfully disabled Dynamic DNS: %s", result["data"])
    else:
        logging.info("Error disabling Dynamic DNS: %s", result["error"])


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


def get_mode_params(mode: str):
    enable_mode, disable_mode, update_mode = False, False, False
    if mode == "get":
        enable_mode = True
    elif mode == "delete":
        disable_mode = True
    elif mode == "update":
        update_mode = True
    elif mode == "refresh":
        enable_mode = True
        update_mode = True

    logging.info("Mode value: %s. Flags set to enable_mode: %s, disable_mode: %s, update_mode: %s",
                 mode, enable_mode, disable_mode, update_mode)
    return (enable_mode, disable_mode, update_mode)


def call_update_url(url: str):
    # Invoke URL to make the change to the DNS record
    result = rest_utils.get_rest_endpoint(url)

    if result["success"]:
        logging.info("Updated Dynamic DNS successfully")
    else:
        logging.info("Error updating Dynamic DNS: %s", result["error"])


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
    mode = os.getenv("MODE")
    update_url = os.getenv("UPDATE_URL")

    logging.info("Update URL in config set to: %s", update_url)

    # Set mode flags from the config
    (enable_mode, disable_mode, update_mode) = get_mode_params(mode)

    # Error is the domain that is to be updated has not been specified
    if (target_domain is None) or (len(target_domain) == 0):
        raise ValueError("Target zone not specified", target_domain)

    # Check if current public IP of connection is same as DNS. Only update if they differ.
    if dns_utils.is_public_ip_up_to_date(target_domain) is False:
        logging.info("Public IP and DNS do not match - performing processing")

        logging.info("Loading API key and target domain from environment")
        headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        # Allow option to disable Dynamic DNS before making update, in case a full reset is required
        if disable_mode:
            logging.info("Config: Disabling Dynamic DNS before updating")
            disable_dynamic_dns(headers)

        if enable_mode:

            logging.info(
                "Calling IONOS API to get update URL for domain %s", target_domain)

            # Invoke DynamicDNS API to configure for current public IP
            result = update_dynamic_dns(headers, target_domain)
            if result["success"]:
                logging.info("Dynamic DNS API call successful")
                logging.debug("API payload returned: %s", result["data"])
            else:
                logging.info(
                    "Error rertieving Dynamic DNS URL: %s", result["error"])

            # Grab URL from response that needs called to invoke the update
            dyn_update_data = result["data"]
            update_url = dyn_update_data["updateUrl"]

            logging.info("Update URL extracted from response: %s",
                         update_url)

        if update_mode:
            if update_url is None:
                logging.error(
                    "No update URL specified. Update will not be performed")
            else:
                logging.info("Calling update URL to update DynDNS")
                call_update_url(update_url)

    else:
        logging.info("No Dynamic DNS update required.")


main()
