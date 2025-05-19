# Ionos Scripts

Python script that allow Dynamic DNS update for a domain using the [Ionos Developer API](https://developer.hosting.ionos.com) for [DNS](https://developer.hosting.ionos.com/docs/dns).

This allows the kind of updates you'd normally see through a system like DynDNS, but using domains that are hosted on Ionos. Ionos provides the API's that enable all this, this script just calls them, and wraps it in a process that will only do that if an update is needed.

Intended usage is to install this on a server on your network, running this periodically via cron or other scheduler to update the DNS record to point to the right Public IP if it changes.

## Usage

`python update_dns.py`

This will do a number of things:

-   look up DNS to find IPv4 address of current DNS `A` record
-   query external API to find public IP address of current connection
-   compare `A` record and public IP to see if they match
-   if addresses are different, call the IONOS Dynamic DNS API to update DNS record to match current public IP

## Config

Configuration is stored in a `.env` file in the same directory as the script. There are 2 important config parameters.

| Parameter | Meaning                                      | Example                            |
| --------- | -------------------------------------------- | ---------------------------------- |
| API_KEY   | Ionos API Key in the format `id.secret`      | `abcd34a67.hKy7JHfgltyrewokm#hfgm` |
| DOMAIN    | The domain name to be updated for DynamicDNS | `example.com`                      |

The IONOS API key must be created from your account. This will give you the info to put in the `.env` file, allowing auth with the Ionos API.

Instructions for how to do this are given on the [IONOS Developer Portal](https://developer.hosting.ionos.com/docs/getstarted).
