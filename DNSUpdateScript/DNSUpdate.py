#!/usr/bin/python3

"""
    Set
    Philippe Ilharreguy
    Updated 03-09-2015
 
 
    Quick Linux DNS IP Updater Python script for FreeDNS (freedns.afraid.org)
    The script get the first external IP retrieved from one of 5 ip servers. Then if
    new external ip is different from preview's one it update freeDNS server IP. Finally
    it write to a log file the update procedure.
    http://www.danielgibbs.net/
    https://gist.github.com/jfrobbins/6085917
    http://stackoverflow.com/questions/845058/how-to-get-line-count-cheaply-in-python
    Must set update_key and make sure that ip_file is read and writable
 """
import sys
import os
import requests
import time

# FreeDNS Update Key
update_key = "YWxncGM0a1U1Qks3QWF3VUIxOUQ6MTkwMzYyNTg="
# FreeDNS Update URL
update_freedns_url = "http://freedns.afraid.org/dynamic/update.php?" + update_key


# Use these IP server URLs, because they return all the same IP format (plain text),
# so IP can be retreived with the same method
ip_urls = ['http://api.ipify.org',
           'http://ip.dnsexit.com',
           'http://www.icanhazip.com']

# Retrieved IP strings are cleaned by this function
def ip_str_clean(ip_str):
    ip_str = str(ip_str)
    ip_str = ip_str.replace("\n", "")
    ip_str = ip_str.replace("\r", "")
    ip_str = ip_str.replace(" ", "")
    return ip_str


# Store the first IP response retrieved from URLs
public_ip = ""
# Store preview public IP
preview_public_IP = ""

for ip_url in ip_urls:
    try:
        print(ip_url)
        req_ip = requests.get(ip_url, timeout=5)
        if req_ip.ok == True:
            public_ip = ip_str_clean(req_ip.text)
            print('Your IP is: ', public_ip)
            break   # Stop for loop when the first external ip is retrieved

        else:
            print('Website not working well. No IP retrieved.')
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as err:
        print('Server taking too long. Probably is down.')
    except:
        print("Unexpected error:", sys.exc_info()[0])

# Exit progrm if public_ip doesn't match the ip format.
# An error must ocurred retrieving the ip from the servers.
if len(public_ip)<7:    # ip string length >= 7 is good. EX: 1.1.1.1
    sys.exit("Servers didn't return any ip. Execution stoped.")


# The file where the last known public IP is written
ip_file = ".freedns_ip"
# Save IP updates
log_ip_update_file = "log_ip_update"

# Create the file if it doesnt exist, otherwise read preview public IP
if not os.path.exists(ip_file):
    fh = open(ip_file, "w")
    fh.write(public_ip)
    fh.close()
    preview_public_ip = "Unknown"
    print("Created FreeDNS IP log file: " + ip_file)
else:
    fh = open(ip_file, "r")
    preview_public_ip = fh.read()
    fh.close()
    preview_public_ip = ip_str_clean(preview_public_ip)

# Update IP only if current IP is different from preview's one
if preview_public_ip != public_ip:
    # Update IP in freeDNS server
    requests.get(update_freedns_url)

    # Save new public ip
    fh = open(ip_file, "w")
    fh.write(public_ip)
    fh.close()

    # Create log file
    date_ip_update_str = time.strftime('%d/%m/%Y %H:%M:%S')
    log_str = date_ip_update_str + "   New public IP is " + public_ip + ". Preview public IP was " + preview_public_ip + ".\n"
    print(log_str)

    # Read file to count how many lines it has
    fh = open(log_ip_update_file, "a+")
    file_lines = fh.readlines()
    file_lines_count = len(file_lines)
    fh.close()

    if file_lines_count >= 5:
        fh = open(log_ip_update_file, "w")
        file_lines = file_lines[1:5]
        file_lines.append(log_str)
        fh.writelines(file_lines)
        fh.close()

    else:
        fh = open(log_ip_update_file, "a")
        fh.write(log_str)
        fh.close()
else:
    print("The public IP hasn't changed. DNS IP update not necessary.")
