#!/usr/bin/python
# coding=utf-8
#
# Copyright (C) 2018-2024 by dream-alpha
#
# In case of reuse of this source code please do not remove this copyright.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# For more information on the GNU General Public License see:
# <http://www.gnu.org/licenses/>.


import os
import socket
from Components.config import config
from .Debug import logger


BUFFER = 8192


def sock2int(sock_string):
	sock_string = sock_string.split("\n")[0]
	sock_int = int(sock_string)
	return sock_int


def int2sock(sock_int):
	sock_string = str(sock_int) + "\n"
	return sock_string


def createServerSocket(host, port):
	server_socket = None
	try:
		socket.inet_aton('%s %s' % (host, int(port)))
	except socket.error:
		logger.debug("invalid ip: %s, port: %s", host, port)
		return None
	try:
		server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		server_socket.bind((host, int(port)))
		server_socket.listen(5)
		logger.debug("socket server started on port: %s", port)
	except Exception as e:
		logger.error("exception: %s", e)
		return None
	return server_socket


def createClientSocket(host, port):
	client_sock = None
	try:
		client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		client_sock.settimeout(5)
		client_sock.connect((host, int(port)))
	except Exception as e:
		logger.debug('Unable to connect: %s', e)
		return None
	logger.debug('client connected to: %s:%s', host, port)
	return client_sock


def sendSocket(sock, data):
	# logger.info("sendSocket: %s", data)
	sent = 0
	try:
		sent = sock.send(data)
	except Exception as e:
		logger.error("exception: %s", e)
	# logger.debug("sendSocket: %s", sent)
	return sent


def sendallSocket(sock, data):
	# logger.info("sendAllSocket: %s", data)
	try:
		sock.sendall(data)
	except Exception as e:
		logger.error("exception: %s", e)


def receiveSocket(sock):
	# logger.info("receiveSocket")
	data = ""
	try:
		data = sock.recv(BUFFER)
	except Exception as e:
		logger.error("exception: %s", e)
	# logger.debug("receiveSocket: %s", len(data))
	return data


def getIpAddress(ifaces):
	for iface in ifaces:
		ifconfig = os.popen("ifconfig %s" % iface).read()
		lines = ifconfig.split("\n")
		ip = "0.0.0.0"
		for line in lines:
			line = line.strip()
			if "inet addr:" in line:
				words = line.split(":")
				ip = words[1].split(" ")[0]
				break
		if iface != "0.0.0.0":
			break
	logger.debug("IP: %s", ip)
	return ip


def pingHost(ip):
	ping = "ping -c1 -w1 " + ip
	result = os.popen(ping).read()
	online = "0 packets received" not in result
	return online


def getClientServerHosts():
	hosts = socket.gethostname()
	if config.plugins.socketcockpit.client.value:
		online = pingHost(config.plugins.socketcockpit.server_ip_address.value)
		if online:
			server = socket.gethostbyaddr(config.plugins.socketcockpit.server_ip_address.value)
			if server:
				server = server[0]
				if "." in server:
					server = server.split(".")[0]
				hosts += "/" + server
	return hosts
