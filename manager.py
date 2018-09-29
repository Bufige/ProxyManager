
import math
from getData import *
from proxy import Proxy
from database import DB
from config import TOTAL_THREADS



class Manager:
	def __init__(self):
		self.db = DB()
		self.ips = []
		self.getIps()

	##
	## @brief      adds all the new proxies found...
	##
	## @param      self  The object
	##
	##
	def add(self):
		print('STARTING TO BENCHMARK PROXIES...\n')
		
		posProcessed = 1
	
		ips = self.newUniqueIps()
	
		posEnd = len(ips)

		if posEnd == 0:
			print('No new proxy to be added!')
			return None

		threadList = []
		threadId = 1

		ipsPerThread = max(math.ceil(posEnd/TOTAL_THREADS), 1)

		print('Currently running {} threads'.format(int(posEnd/ipsPerThread)))
		for chunk in self.chunks(ips, ipsPerThread):			
			threadList.append(Proxy(chunk, threadId))
			threadId += 1

		for thread in threadList:
			thread.start()
		for thread in threadList:
			thread.join()

		# total of proxies.
		proxies = {}
		# total of proxies that failed.
		proxiesFailed = []
		# get all the proxies from all the threads.
		for item in threadList:
			for proxy in item.proxies:
				if len(proxy) > 3:
					proxies[proxy] = item.proxies[proxy]
			for proxy in item.proxiesFailed:
				if len(proxy) > 3:
					proxiesFailed.append(proxy)

		if len(proxies) > 0:
			print('{} new proxies were added!'.format(len(proxies)))
			self.db.insertIntoTable(proxies)

		if len(proxiesFailed) > 0:
			print('{} proxies failed...'.format(len(proxiesFailed)))
			for proxy in proxiesFailed:			
				self.db.deleteProxy(proxy)
	def update(self, speed = None):

		ips = list(self.db.getExistingProxies())
				
		posProcessed = 1
	
		posEnd = len(ips) 

		print("Updating proxies from database...")

		threadList = []
		threadId = 1

		ipsPerThread = max(int(posEnd/TOTAL_THREADS), 1)

		print('Currently running {} threads'.format(int(posEnd/ipsPerThread)))
		for chunk in self.chunks(ips, ipsPerThread):			
			threadList.append(Proxy(chunk, threadId))
			threadId += 1

		for thread in threadList:
			thread.start()
		for thread in threadList:
			thread.join()

		# total of proxies.
		proxies = {}
		# total of proxies that failed.
		proxiesFailed = []
		# get all the proxies from all the threads.
		for item in threadList:
			for proxy in item.proxies:
				if len(proxy) > 3:
					if speed == None or item.proxies[proxy] < speed:
						proxies[proxy] = item.proxies[proxy]
					else:
						proxiesFailed.append(proxy)
			for proxy in item.proxiesFailed:
				if len(proxy) > 3:
					proxiesFailed.append(proxy)

		if len(proxies) > 0:
			print('{} were updated!'.format(len(proxies)))
			for ip in proxies:
				self.db.updateProxy(ip, proxies[ip])

		if len(proxiesFailed) > 0:
			print('{} proxies failed and were removed...'.format(len(proxiesFailed)))
			for proxy in proxiesFailed:			
				self.db.deleteProxy(proxy)

	##
	## @brief      removes the slower proxies above the speed. 
	##
	## @param      self   The object
	## @param      speed  The speed in seconds...
	##
	##
	def delete(self, speed):
		if speed != None:
			ips = list(self.db.getSpeedEqualOrHigher(speed))
			if len(ips) > 0:
				print('{} were slower than {} seconds and were removed...'.format(len(ips), speed))
				for ip in ips:
					self.db.deleteProxy(ip)

	##
	## @brief      retries to add every proxy seen so far save in the files.
	##
	## @param      self  The object
	##
	##
	def reTry(self):		
		ips = self.ips

		posEnd = len(ips)

		print("{} were seen so far, retrying to add them...".format(posEnd))


		if posEnd == 0:
			print('No new proxy to be added!')
			return None

		threadList = []
		threadId = 1

		ipsPerThread = max(math.ceil(posEnd/TOTAL_THREADS), 1)

		print('Currently running {} threads'.format(int(posEnd/ipsPerThread)))
		for chunk in self.chunks(ips, ipsPerThread):			
			threadList.append(Proxy(chunk, threadId))
			threadId += 1

		for thread in threadList:
			thread.start()
		for thread in threadList:
			thread.join()

		# total of proxies.
		proxies = {}
		# total of proxies that failed.
		proxiesFailed = []
		# get all the proxies from all the threads.
		for item in threadList:
			for proxy in item.proxies:
				if len(proxy) > 3:
					proxies[proxy] = item.proxies[proxy]
			for proxy in item.proxiesFailed:
				if len(proxy) > 3:
					proxiesFailed.append(proxy)

		if len(proxies) > 0:
			print('{} new proxies were added!'.format(len(proxies)))
			self.db.insertIntoTable(proxies)

		if len(proxiesFailed) > 0:
			print('{} proxies failed...'.format(len(proxiesFailed)))
			for proxy in proxiesFailed:			
				self.db.deleteProxy(proxy)

	
	##
	## @brief      call all new added class's to get the proxies.
	##
	## @param      self  The object
	##
	##
	def getIps(self):
		# get the proxies from freeproxylist.
		freeProxyList = FreeProxyList()
		ips0 = freeProxyList.getListProxies()
		for url in ips0:
			self.ips.append(url)

	##
	## @brief      gets all the unique ips that will be added.
	##
	## @param      self  The object
	##
	##
	def newUniqueIps(self):
		currentProxies = self.db.getExistingProxies()
		currentDeletedProxies = self.db.getDeletedProxies()
		return list((set(self.ips) - currentProxies) - currentDeletedProxies)

	def chunks(self,l, n):
		for i in range(0, len(l), n):
			yield l[i:i+n]