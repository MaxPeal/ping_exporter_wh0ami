#! /usr/bin/python3
# -*- coding: utf-8 -*-

#     Dev: wh0ami
# Licence: Public Domain <https://unlicense.org>
# Project: https://codeberg.org/wh0ami/lsp_bot

# Python3 Prometheus Exporter for pinging your systems
# ping exporter webserver

from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import socket
from pathlib import Path
import json
import sys
from urllib.parse import urlparse, parse_qs
import pingexporter

# check whether a config exists
try:
  configfile = sys.argv[1]
  if not Path(configfile).is_file():
    raise Excpetion()
except:
  raise Exception("[Error] Config not found! Usage: ./exporter.py <config>")
  sys.exit(1)

# try to load the config
try:
  with open(configfile, "r") as infile:
    config = json.load(infile)["config"]
except:
  raise Exception("Error while opening the config file!")
  sys.exit(1)

# create a custom class for the webserver
# standard functions (GET and POST request) are overwritten by our own procedures
class exporter(BaseHTTPRequestHandler):
  global config

  def do_GET(self):
    if self.path.startswith("/?") or self.path.startswith("/metrics?"):
      self.send_response(200)
      self.send_header("Content-type", "text/plain")
      self.end_headers()

      output = "# ping exporter for prometheus\n"
      try:
        target = parse_qs(urlparse(self.path).query)["target"][0]
        output += pingexporter.getMetrics(target, config)
      except KeyError:
        output += "# for pinging, send GET variable target!"
      finally:
        self.wfile.write(bytes(output, "utf-8"))
    else:
      self.send_response(404)

  def do_POST(self):
    self.do_GET()

class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass

if __name__ == "__main__":
    webServer = ThreadingSimpleServer((config["ip"], config["port"]), exporter)
    print("Ping Exporter for Prometheus started at http://%s:%s" % (config["ip"], config["port"]))

    try:
      while True:
        webServer.handle_request()
    except KeyboardInterrupt:
      pass

    webServer.server_close()
    print("\nPing Exporter for Prometheus stopped")
