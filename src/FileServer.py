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
import threading
import select
from .Debug import logger
from .SocketUtils import int2sock, createServerSocket, sendSocket, receiveSocket, BUFFER


class FileServer(threading.Thread):

	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.stop_event = threading.Event()
		threading.Thread.__init__(self)

	def join(self, _timeout=None):
		self.stop_event.set()
		threading.Thread.join(self)

	def sendFile(self, sock, filename):
		filesize = 0
		if os.path.exists(filename):
			filesize = os.path.getsize(filename)
		sendSocket(sock, int2sock(filesize))
		readsize = 0
		with open(filename, "rb") as f:
			while readsize < filesize:
				chunk = f.read(BUFFER)
				size = sendSocket(sock, chunk)
				# logger.debug("sent: %s", size)
				if size > 0:
					readsize += size
				else:
					logger.debug("sendSocket failed.")
					break
		logger.debug("file transfer " + "done." if readsize == filesize else "aborted.")

	def run(self):
		server_socket = createServerSocket(self.host, self.port)
		if not server_socket:
			return
		connection_list = [server_socket]
		while not self.stop_event.isSet():  # pylint: disable=W1505
			read_sockets, _write_sockets, _error_sockets = select.select(connection_list, [], [], 1)
			for sock in read_sockets:
				if sock == server_socket:
					conn, address = sock.accept()
					connection_list.append(conn)
					logger.debug(("client (%s, %s) connected"), address[0], address[1])
				else:
					connection_list.remove(sock)
					filename = receiveSocket(sock)
					logger.debug("received request: %s", filename)
					self.sendFile(sock, filename)
					logger.debug("closing socket")
					sock.close()
		server_socket.close()
