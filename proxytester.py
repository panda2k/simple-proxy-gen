import requests
import time
from requests.auth import HTTPProxyAuth
from requests.exceptions import ProxyError

def test_proxy(proxy_ip, proxy_username, proxy_password, proxy_port):
    proxies = {
        "http": f"http://{proxy_ip}:{proxy_port}",
        "https": f"https://{proxy_ip}:{proxy_port}"
    }
    proxy_auth = HTTPProxyAuth(proxy_username, proxy_password)
    requests_client = requests.Session()
    requests_client.proxies = proxies
    requests_client.auth = proxy_auth

    while True:
        try:
            requests_client.get("http://checkip.dyndns.org")
            return True
        except ProxyError:
            return False

def main():
    proxy_ip = input("Please input the proxy ip: ")
    test_proxy(proxy_ip, "pwbo", "pwbo", "80")

if __name__ == "__main__":
    main()
