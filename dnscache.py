#!/usr/bin/python3
# -*- coding: utf-8 -*-

#     Dev: wh0ami
# Licence: Public Domain <https://unlicense.org>
# Project: https://codeberg.org/wh0ami/lsp_bot

# Python3 Prometheus Exporter for pinging your systems
# dns caching unit

import socket
import time

# create a cache
dnscache = {}


def nslookup(domain):
    global dnscache
    ttl = 86400

    # check whether the domain was cached ever before
    if domain in dnscache:
        # if the domain has expired, update the cache
        now = int(round(time.time(), 0))
        if now > dnscache[domain]["expires"]:
            dnscache[domain]["ip"] = host(domain)
            dnscache[domain]["expires"] = now + ttl
    else:
        # get the ip for the domain and write it to the cache
        dnscache[domain] = {}
        dnscache[domain]["ip"] = host(domain)
        now = int(round(time.time(), 0))
        dnscache[domain]["expires"] = now + ttl

    # return the ip for the domain
    return dnscache[domain]["ip"]


def host(domain):
    ip = socket.gethostbyname(domain)
    return ip
