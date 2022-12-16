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


import threading
from .Debug import logger
from .SocketUtils import sock2int, createClientSocket, sendSocket, receiveSocket


class FileClient(threading.Thread):

	def __init__(self, host, port, source, destination):
		logger.info("host: %s, port: %s, source: %s, destination: %s", host, port, source, destination)
		self.host = host
		self.port = port
		self.source = source
		self.destination = destination
		self.stop_event = threading.Event()
		self.is_file_streaming = False
		threading.Thread.__init__(self)

	def join(self, _timeout=None):
		self.stop_event.set()
		threading.Thread.join(self)

	def isFileStreaming(self):
		return self.is_file_streaming

	def run(self):
		sock = createClientSocket(self.host, self.port)
		if not sock:
			return
		if sendSocket(sock, self.source):
			filesize = 0
			writesize = 0

			filesize = sock2int(receiveSocket(sock))
			logger.debug("received filesize: %d", filesize)

			self.is_file_streaming = True
			with open(self.destination, "w") as f:
				while not self.stop_event.isSet():  # pylint: disable=W1505
					chunk = receiveSocket(sock)
					# logger.debug("chunk size: %s", len(chunk))
					if chunk:
						f.write(chunk)
						writesize += len(chunk)
						if writesize == filesize:
							logger.debug("file transfer completed.")
							break
					else:
						logger.debug("file transfer terminated.")
						break
		else:
			logger.debug("sending filename failed, exiting.")

		self.is_file_streaming = False
		logger.debug("closing socket")
		sock.close()
