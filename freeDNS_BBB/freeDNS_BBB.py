#!/usr/bin/python

"""
    Updated 03-07-2014
    SET
    Philippe Ilharreguy
 
 
    Quick Linux Python script for FreeDNS IP update (freedns.afraid.org).
    The script get the first external IP retrieved from one of 5 ip servers. Then if
    new external ip is different from preview's one it update freeDNS server IP. Finally
    it write to a log file the update procedure.

    http://www.danielgibbs.net/
    https://gist.github.com/jfrobbins/6085917
    http://stackoverflow.com/questions/845058/how-to-get-line-count-cheaply-in-python

    Must set update_key and make sure that ip_file is read and writable
 """

import os
import requests
import time

# FreeDNS Update Key
update_key = "YmM3akpzVG9zbTJvTUQ3VTNpbE9mazZVOjEyMDExMTgw"
# FreeDNS Update URL
update_freedns_url = "http://freedns.afraid.org/dynamic/update.php?" + update_key


# Use these IP server URLs, because they return all the same IP format (plain text),
# so IP can be retreived with the same method
ip_urls = ['http://api.ipify.org',
           'http://curlmyip.com',
           'http://ip.dnsexit.com',
           'http://www.icanhazip.com',
           'http://www.danielgibbs.net/ip.php']

# Retrieved IP strings are cleaned by this function
def ip_str_clean(ip_str):
    ip_str = str(ip_str)
    ip_str = ip_str.replace("\n", "")
    ip_str = ip_str.replace("\r", "")
    ip_str = ip_str.replace(" ", "")
    return ip_str


# Store the first IP response retrieved from URLs
external_ip = ""

for ip_url in ip_urls:
    try:
        print ip_url
        req_ip = requests.get(ip_url)

        if req_ip.ok == True:
            external_ip = ip_str_clean(req_ip.text)
            print 'Your IP is:', external_ip
            break   # Stop for loop when the first external ip is retrieved

        else:
            print 'Website not working well. No IP retrieved.'

    except requests.exceptions.RequestException as e:    # This is the correct syntax
        print e


# The file where the last known external IP is written
ip_file = ".freedns_ip"
# Save IP updates
log_ip_update_file = "log_ip_update"

# Create the file if it doesnt exist, otherwise update old IP
if not os.path.exists(ip_file):
    with open(ip_file, "w") as fh:
        fh.write(external_ip)
    preview_external_ip = "Unknown"
    print "Created FreeDNS IP log file: " + ip_file

else:
    with open(ip_file, "r") as fh:
        preview_external_ip = fh.read()
	preview_external_ip = preview_external_ip.rstrip('\n')

# Update IP only if current IP is different from preview's one
if preview_external_ip != external_ip:
    # Update IP in freeDNS server
    requests.get(update_freedns_url)
    
    # Save new external ip
    with open(ip_file, "w") as fh:
        fh.write(external_ip)
    
    # Create log file
    date_ip_update_str = time.strftime('%d/%m/%Y %H:%M:%S')
    log_str = date_ip_update_str + "   New external IP is " + external_ip + ". Preview external IP was " + preview_external_ip + ".\n"
    print log_str
    
    # Read file to count how many lines there are
    with open(log_ip_update_file, "a+") as fh:
        file_lines = fh.readlines()
        file_lines_count = len(file_lines)
    
    if file_lines_count >= 5:
        with open(log_ip_update_file, "w") as fh:
            file_lines = file_lines[1:5]
            file_lines.append(log_str)
            fh.writelines(file_lines)
    else:
        with open(log_ip_update_file, "a") as fh:
            fh.write(log_str)
else:
    print "The external IP hasn't changed. DNS IP update not necessary."