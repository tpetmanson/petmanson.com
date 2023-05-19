import re
import requests
from requests.auth import HTTPBasicAuth
import logging
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

zone_api_key = ""
basic = HTTPBasicAuth('tpetmanson', zone_api_key)

def get_current_ip() -> str:
    current_ip = requests.get("https://ident.me").text
    assert re.fullmatch(r"\d+\.\d+\.\d+\.\d+", current_ip)
    return current_ip


def get_dns_record(main_domain: str, domain: str) -> str:
  response = requests.get(f"https://api.zone.eu/v2/dns/{main_domain}/a", auth=basic)
  assert response.status_code == 200
  record = [record for record in response.json() if record["name"] == domain][0]
  return record

current_ip = get_current_ip()
logger.info(f"Current IP address is {current_ip}")
for domain in ["petmanson.com", "mandarones.com", "api.mandarones.com"]:
   main_domain = domain
   if domain == "api.mandarones.com":
      main_domain = "mandarones.com"
   record = get_dns_record(main_domain, domain)
   domain_ip = record["destination"]
   logger.info(f"Domain {domain} has IP address {domain_ip}")
   if current_ip != domain_ip:
      logger.info(f"Updating domain {domain} IP address from {domain_ip} to {current_ip}")
      response = requests.put(f"https://api.zone.eu/v2/dns/{main_domain}/a/{record['id']}", 
                              json={"name": domain, "destination": current_ip}, 
                              auth=basic)
      assert response.status_code == 200
logger.info("Done.")
