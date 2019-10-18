#! /usr/bin/python3
# -*- coding: utf-8 -*-

#     Dev: wh0ami
# Licence: Public Domain <https://unlicense.org>
# Project: https://codeberg.org/wh0ami/ping_exporter

# Python3 Prometheus Exporter for pinging your systems
# ping library

import re
import subprocess

# function for removing the port from the ip or domain, if there is a port given

def ip_port(ip):
  # RegEx explanation:
  # not re.search('[:]', ip) --> simple, everything without a : couldnt hava a port; tis works for ipv4 and domains
  # ip.count(':') == 7 and not re.search('[:]{2}', ip) --> a regular ipv6 without a port have 7 : and no ::
  # re.search('[:]{2}[a-dA-F0-9]{1,4}$', ip) --> a short ipv6 will end with :: plus 4 chars (numeric or a-f|A-F)
  if ((not re.search('[:]', ip)) or (ip.count(':') == 7 and not re.search('[:]{2}', ip)) or (re.search('[:]{2}[a-fA-F0-9]{1,4}$', ip))):
    return ip
  else:
    cutted = re.sub('[:][0-9]{1,5}$', '', ip);
    return cutted

# check, if the given string is a ipv4 address

def valid_ipv4(ip):
  if re.search('^((1?[0-9]?[0-9]|2([0-4][0-9]|5[0-5]))[.]){3}(1?[0-9]?[0-9]|2([0-4][0-9]|5[0-5]))', ip):
    return True
  else:
    return False

# check, if the given string is a ipv6 address

def valid_ipv6(ip):
  if re.search('^(([0-9a-fA-F]{1,4}[:]){7}[0-9a-fA-F]{1,4}|^([0-9a-fA-F]{1,4}[:]){1,6}[:][0-9a-fA-F]{1,4}|^[:]{2}[0-9a-fA-F]{1,4})', ip):
    return True
  else:
    return False

# check, if the given string is a domain
# source for regex: https://blog.bejarano.io/domain-name-validation-with-regular-expressions.html

def valid_domain(domain):
  if domain == "localhost" or re.search('^(?=.{4,255}$)([a-zA-Z0-9_]([a-zA-Z0-9_-]{0,61}[a-zA-Z0-9_])?\.){1,126}[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]$', domain):
    return True
  else:
    return False




def getMetrics(target, config):
  output = ""

  # remove port from the input
  target = ip_port(target)

  # valide, whether the target is a ipv4, a ipv6 or a domain
  if valid_ipv4(target) or valid_ipv6(target) or valid_domain(target):
    # build and execute a command for pinging
    p = subprocess.Popen(["ping", "-c", str(config["packet_count"]), "-i", str(config["interval_ms"]/1000), "-s", str(config["packet_bytes"]), "-W", str(config["timeout_ms"]/1000), target], stdout=subprocess.PIPE, universal_newlines=True)
    p.wait()
    raw = p.communicate()[0]

    raw = raw.split("\n")
    lines = len(raw)

    packets = raw[lines - 3].split()
    output += 'ping_packets{type="transmitted"} ' + str(packets[0]) + "\n"
    output += 'ping_packets{type="received"} ' + str(packets[3]) + "\n"
    output += 'ping_packets{type="lost"} ' + str(int(packets[0]) - int(packets[3])) + "\n"
    output += 'ping_packet_loss_percent{} '+ str(packets[5].replace("%", '')) + "\n"

    if raw[lines - 2].startswith('rtt'):
      rtt = raw[lines - 2].split()[3].split("/")
      output += 'ping_rtt_ms{type="min"} ' + str(rtt[0]) + "\n"
      output += 'ping_rtt_ms{type="avg"} ' + str(rtt[1]) + "\n"
      output += 'ping_rtt_ms{type="max"} ' + str(rtt[2]) + "\n"
      output += 'ping_rtt_ms{type="mdev"} ' + str(rtt[3]) + "\n"

    if config["show_config"]:
      output += 'ping_config{option="interval_ms"} ' + str(config["interval_ms"]) + "\n"
      output += 'ping_config{option="timeout_ms"} ' + str(config["timeout_ms"]) + "\n"
      output += 'ping_config{option="packet_bytes"} ' + str(config["packet_bytes"]) + "\n"
      output += 'ping_config{option="packet_count"} ' + str(config["packet_count"]) + "\n"
      output += 'ping_config{target="' + str(target) + '"} 0' + "\n"

  return output
