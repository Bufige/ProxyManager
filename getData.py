import os
import requests




class FreeProxyList:
	def __init__(self):
		self.URL = 'https://github.com/a2u/free-proxy-list/raw/master/free-proxy-list.txt'
		self.FILE_PROXIES = 'proxies.txt'

	##
	## @brief      Gets the list proxies.
	##
	## @return     The list proxies.
	##
	def getListProxies(self):
		proxiesOld = []
		proxiesNew = []
		# file exists.
		if os.path.exists(self.FILE_PROXIES):
			# try to load the proxies.
			file = open(self.FILE_PROXIES , "r")

			for proxy in file:
				if len(proxy) > 1:
					proxiesOld.append(proxy.strip())
			file.close()
		
		# get the req.
		req = requests.get(self.URL)
		#split the the data into lines.
		page = req.text.split('\n')
		pos = 0
		for line in page:
			if len(line) > 1:				
				proxiesNew.append(line.strip())

		# save the data.
		file = open(self.FILE_PROXIES, 'w+')
		# data must be unique.
		proxies = set(proxiesOld).union(proxiesNew)
		tmp = []
		for proxy in proxies:
			if len(proxy) > 1:
				file.write('{}\n'.format(proxy.strip()))
				tmp.append(proxy.strip())
		file.close()
		return tmp
