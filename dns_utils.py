import rest_utils
import logging
import socket

DNS_ZONES_API = "https://api.hosting.ionos.com/dns/v1/zones"
IPIFY_PUBLIC_API = "https://api.ipify.org"

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)


def get_a_record(headers, target_domain):

    # get list of zones
    result = rest_utils.get_rest_endpoint(DNS_ZONES_API, headers)

    logging.debug("Zone data: %s", result)

    # from list of zones, extract the target zone and save the zone id
    target_zone = filter_zone_results(result)
    if target_zone is None:
        print("Zone does not exist, processing stopped")
        raise ValueError("Target zone does not exist", target_domain)

    # get details of the zone id saved
    zone_details = get_zone_details(target_zone['id'], headers)
    logging.debug("Zone details for %s: %s", target_domain, zone_details)

    # A Record is
    a_record = filter_zone_records(zone_details['records'])
    logging.debug("A record is %s", a_record)

    return a_record


def get_zone_details(id, headers):
    result = rest_utils.get_rest_endpoint(
        f"https://api.hosting.ionos.com/dns/v1/zones/{id}", headers)

    return result


def is_a_record(zone_entry):
    return zone_entry['type'] == "A"


def is_target_domain(zone, target_domain):
    return zone['name'] == target_domain


def filter_zone_records(zone):
    # Get back first entry matching A record - should only be one for each unique domain. Returns None if no match
    try:
        a_record = next(filter(is_a_record, zone))
    except StopIteration:
        a_record = None
    return a_record


def filter_zone_results(zones):
    # Get back first entry matching domain - should only be one for each unique domain. Returns None if no match
    try:
        target_zone = next(filter(is_target_domain, zones))
    except StopIteration:
        target_zone = None
    return target_zone


def lookup_dns(hostname):
    ip_address = socket.gethostbyname(hostname)
    return ip_address


def get_public_facing_ip():
    public_ip = rest_utils.get_rest_endpoint(IPIFY_PUBLIC_API)
    return public_ip


def is_public_ip_up_to_date(hostname):

    # Check current DNS IP for hostname
    dns_ip = lookup_dns(hostname)
    logging.debug("DNS returned IP %s for %s", dns_ip, hostname)

    # Get details of public facing IP
    public_ip = get_public_facing_ip()
    logging.debug("Public facing IP is currently set as %s", public_ip)

    if public_ip == dns_ip:
        logging.info("Public IP and DNS record match (%s, %s)",
                     hostname, public_ip)
        return True
    else:
        logging.info("Public IP and DNS record mismatch (Host: %s, DNS: %s, Public IP: %s)",
                     hostname, dns_ip, public_ip)
        return False
