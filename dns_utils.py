
"""
Utility methods to query DNS details about a domain. Implementations that pull
back public facing IP address using external services, that query details from
the IONOS Developer API, and that use Python DNS to pull back IP mapping
"""
import logging
import socket
import rest_utils

DNS_ZONES_API = "https://api.hosting.ionos.com/dns/v1/zones"
IPIFY_PUBLIC_API = "https://api.ipify.org"

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)


def get_a_record_ionos(headers, target_domain):
    """
    Uses the IONOS Developer DNS API to return the A record for a given domain
    """

    # get list of zones
    result = rest_utils.get_rest_endpoint(DNS_ZONES_API, headers)

    logging.debug("Zone data: %s", result)

    # from list of zones, extract the target zone and save the zone id
    target_zone = filter_zone_results(result)
    if target_zone is None:
        print("Zone does not exist, processing stopped")
        raise ValueError("Target zone does not exist", target_domain)

    # get details of the zone id saved
    zone_details = get_zone_details_ionos(target_zone['id'], headers)
    logging.debug("Zone details for %s: %s", target_domain, zone_details)

    # A Record is
    a_record = filter_zone_records(zone_details['records'])
    logging.debug("A record is %s", a_record)

    return a_record


def get_zone_details_ionos(zone_id, headers):
    """
    Perform the Query against the IONOS DNS API to return details of a particular
    zone given the IONOS Zone ID
    """
    return rest_utils.get_rest_endpoint(f"{DNS_ZONES_API}/{zone_id}", headers)


def is_a_record(zone_entry):
    """
    Filter method Zone detail entries returned from IONOS Zone Query to extract the 'A' record
    """
    return zone_entry['type'] == "A"


def is_target_domain(zone, target_domain):
    """
    Filter method for zone summary entries returned from Ionos DNS Query to
    extract details including zone ID for specified domain
    """
    return zone['name'] == target_domain


def filter_zone_records(zone):
    """
    Perform filtering of results to extract 'A' record from zone detail results.
    Gets back first matching 'A' record. Assumption is there is only one
    Returns None if not match.
    """
    try:
        a_record = next(filter(is_a_record, zone))
    except StopIteration:
        a_record = None
    return a_record


def filter_zone_results(zones):
    """
    Perform filtering of results to extract Zone details from Zone summary results
    Gets back first entry matching domain - should only be one for each unique domain.
    Returns None if no match
    """
    try:
        target_zone = next(filter(is_target_domain, zones))
    except StopIteration:
        target_zone = None
    return target_zone


def lookup_dns(hostname) -> str | None:
    """
    Return IP address for DNS hostname using Python socket libs
    """
    try:
        ip_address = socket.gethostbyname(hostname)
    except socket.error:
        ip_address = None
    return ip_address


def get_public_facing_ip():
    """
    Use IPIFY public API to query public facing IP
    """
    result = rest_utils.get_rest_endpoint(IPIFY_PUBLIC_API)

    if result["success"]:
        logging.info("Public IP retrieved: %s", result["data"])
        return result["data"]
    else:
        logging.info("Error retrieving public IP", result["error"])
        return None


def is_public_ip_up_to_date(hostname: str) -> bool:
    """
    Lookup DNS for hostname and see if it matches the current public facing IP.
    Returns True if they are both the same, and False if there's a mismatch.
    """
    # Check current DNS IP for hostname
    dns_ip = lookup_dns(hostname)
    logging.debug("DNS returned IP %s for %s", dns_ip, hostname)

    # Get details of public facing IP
    public_ip = get_public_facing_ip()
    logging.debug("Public facing IP is currently set as %s", public_ip)

    if public_ip == dns_ip:
        logging.info("Public IP and DNS record match (%s) for domain %s",
                     public_ip, hostname)
        return True
    else:
        logging.info("Public IP and DNS record mismatch (Host: %s, DNS: %s, Public IP: %s)",
                     hostname, dns_ip, public_ip)
        return False
