import requests
import threading
import timeit


from config import DEBUG,CONNECTION_TIMEOUT,CONNECTION_REPETITION,URL_WEBSITE


class Proxy(threading.Thread):
	def __init__(self, ips, id):
		super(Proxy, self).__init__()
		
		# ips to test against the url
		self.ips = ips
		# thread id
		self.id = id		
		# ip:speed
		self.proxies = {}
		# proxies that failed	
		self.proxiesFailed = []

	def run(self):
		# go through each item.
		for ip in self.ips:			
			# config proxy
			proxy = {'https' : ip}
			
			totalSpeed = 0
			hasFailed = False

			# run times times
			for i in range(0, CONNECTION_REPETITION):
				reqSpeed = self.benchMarkProxy(proxy)
				if reqSpeed == None:
					hasFailed = True
					break
				totalSpeed += reqSpeed

			if not hasFailed:
				self.proxies[ip] = totalSpeed/CONNECTION_REPETITION
			else:
				if DEBUG:
					print('[ERROR] proxy {} failed...'.format(ip))
				self.proxiesFailed.append(ip)

	##
	## @brief      runs the current proxy.
	##
	## @param      self   The object
	## @param      proxy  The proxy
	##
	## @return     true/false or none if request was not finished.
	##
	def benchMarkProxy(self,proxy):
		# benchmark the proxy.
		status = True
		startTime = timeit.default_timer()
		try:
			requests.get(URL_WEBSITE, proxies = proxy,timeout=CONNECTION_TIMEOUT)
		except:
			status = False
		endTime = timeit.default_timer()
		if status:
			return endTime - startTime
		return None
			
