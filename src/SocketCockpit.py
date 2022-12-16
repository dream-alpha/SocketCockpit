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
from Components.config import config
from .Debug import logger
from .RequestServer import RequestServer
from .FileServer import FileServer
from .FileClient import FileClient
from .OnlineMonitor import OnlineMonitor
from .SocketUtils import getIpAddress
from .FileUtils import touchFile, deleteFiles


TMP_PATH = "/media/hdd/movie/remote.ts"
instance = None


class SocketCockpit():

	def __init__(self):
		logger.info("...")
		global instance
		instance = self
		self.request_server_thread = None
		self.file_server_thread = None
		self.file_client_thread = None
		self.online_monitor = OnlineMonitor.getInstance()
		if config.plugins.socketcockpit.client.value:
			self.online_monitor.start()
		if config.plugins.socketcockpit.server.value:
			self.startServer()

	@staticmethod
	def getInstance():
		return instance

	def startServer(self):
		logger.info("...")
		ip_address = getIpAddress(["eth0", "wlan0"])
		if ip_address != "0.0.0.0":
			self.request_server_thread = RequestServer(
				ip_address,
				config.plugins.socketcockpit.request_server_port.value
			)
			self.request_server_thread.start()
			self.file_server_thread = FileServer(
				ip_address,
				config.plugins.socketcockpit.file_server_port.value
			)
			self.file_server_thread.start()

	def stopServer(self):
		logger.info("...")
		if self.request_server_thread:
			self.request_server_thread.join()
			self.request_server_thread = None
		if self.file_server_thread:
			self.file_server_thread.join()
			self.file_server_thread = None

	def stopFileClient(self):
		if self.file_client_thread:
			self.file_client_thread.join()
			deleteFiles(os.path.splitext(TMP_PATH)[0] + ".*")

	def isFileStreaming(self):
		is_file_streaming = False
		if self.file_client_thread:
			is_file_streaming = self.file_client_thread.isFileStreaming()
		return is_file_streaming

	def getFile(self, path):
		logger.info("path: %s", path)
		file_path = path
		if config.plugins.socketcockpit.client.value and self.online_monitor.isOnline():
			file_path = TMP_PATH
			touchFile(file_path)
			self.file_client_thread = FileClient(
				config.plugins.socketcockpit.server_ip_address.value,
				config.plugins.socketcockpit.file_server_port.value,
				path,
				file_path
			)
			self.file_client_thread.start()
		return file_path
