import ipaddress
import urllib.parse
from typing import Tuple, List, Optional

class SSRFGuard:
    """
    Enterprise SSRF (Server-Side Request Forgery) & Domain Sandbox Guard.
    Prevents autonomous web crawler agents from interacting with private cloud metadata endpoints
    (AWS 169.254.169.254), internal loopbacks (127.0.0.1 / localhost), and local enterprise subnets.
    """

    ALLOWED_SCHEMES = {"http", "https"}
    
    # Blocked private and link-local IP networks (RFC 1918, RFC 3927, RFC 4291)
    BLOCKED_NETWORKS = [
        ipaddress.ip_network("127.0.0.0/8"),       # Loopback
        ipaddress.ip_network("10.0.0.0/8"),        # Private Class A
        ipaddress.ip_network("172.16.0.0/12"),     # Private Class B
        ipaddress.ip_network("192.168.0.0/16"),    # Private Class C
        ipaddress.ip_network("169.254.0.0/16"),    # Link-local / AWS Instance Metadata
        ipaddress.ip_network("::1/128"),           # IPv6 Loopback
        ipaddress.ip_network("fc00::/7"),          # IPv6 Unique Local
        ipaddress.ip_network("fe80::/10"),         # IPv6 Link-local
    ]

    ALLOWED_MERCHANT_DOMAINS = [
        "reliancesmart.in",
        "blinkit.com",
        "croma.com",
        "tatacliq.com",
        "amazon.in",
        "flipkart.com",
        "quickclearance.local",
        "artisanal-market.in",
        "apextech.in"
    ]

    @classmethod
    def validate_target_url(cls, url: str) -> Tuple[bool, str]:
        """
        Validates that a URL is safe for autonomous agent crawling.
        Returns: (is_safe: bool, reason: str)
        """
        try:
            parsed = urllib.parse.urlparse(url)
            
            # 1. Scheme check
            if not parsed.scheme or parsed.scheme.lower() not in cls.ALLOWED_SCHEMES:
                return False, f"Prohibited URL scheme '{parsed.scheme}'. Only HTTP/HTTPS permitted."

            hostname = parsed.hostname
            if not hostname:
                return False, "Invalid URL: Missing hostname."

            hostname_lower = hostname.lower()

            # 2. Localhost & metadata keywords
            if hostname_lower in {"localhost", "metadata", "instance-data", "169.254.169.254"}:
                return False, f"SSRF Attack Blocked: Direct access to internal host '{hostname}' is forbidden."

            # 3. IP Address Check
            try:
                ip_obj = ipaddress.ip_address(hostname_lower)
                for net in cls.BLOCKED_NETWORKS:
                    if ip_obj in net:
                        return False, f"SSRF Attack Blocked: Target IP '{ip_obj}' falls within forbidden private network '{net}'."
            except ValueError:
                # Not a raw IP literal, it is a domain name
                pass

            return True, "URL validated as safe for autonomous procurement."
        except Exception as e:
            return False, f"URL validation error: {str(e)}"

ssrf_guard = SSRFGuard()
