import os
import timeit
import sys
import threading

import requests
from multiprocessing import Process

import time

import mysql.connector
from proxy import Proxy
from database import DB



URL_WEBSITE = 'https://www.google.com.br'
URL_PROXIES = ['https://github.com/a2u/free-proxy-list/raw/master/free-proxy-list.txt']
FILE_PROXIES = 'proxies.txt'

DB_HOST = 'localhost'
DB_USERNAME = 'root'
DB_PASSWORD ='12345'
DB_DATABASE = 'proxies'



##
## @brief      benchmark the proxy
##
## @param      ip    The ip
##
## @return     The time which took to get a responder, otheriwse None
##
def benchMarkUrl(ip):
	# benchmark the proxy.
	startTime = timeit.default_timer()
	proxy = Proxy(URL_WEBSITE, ip)
	endTime = timeit.default_timer()
	if proxy:
		return endTime - startTime
	return None


##
## @brief      Gets the list proxies from the urls
##
##
def getListProxies():
	proxiesOld = []
	proxiesNew = []
	# file exists.
	if os.path.exists(FILE_PROXIES):
		# try to load the proxies.
		file = open(FILE_PROXIES , "r")

		for proxy in file:
			if len(proxy) > 1:
				proxiesOld.append(proxy.strip())
		file.close()


	# try to get to all urls that have proxies.
	for url in URL_PROXIES:
		# get the req.
		req = requests.get(url)
		#split the the data into lines.
		page = req.text.split('\n')
		pos = 0
		for line in page:
			if len(line) > 1:				
				proxiesNew.append(line.strip())

	# save the data.
	file = open(FILE_PROXIES, 'w+')
	# data must be unique.
	proxies = set(proxiesOld).union(proxiesNew)
	for proxy in proxies:
		if len(proxy) > 1:
			file.write('{}\n'.format(proxy.strip()))
	file.close()

##
## @brief      loading items
##
## @param      pos   The position
## @param      end   The end
##
##
def loadingItems(pos, end):
	sys.stdout.write('\r')
	sys.stdout.write("Processed {} of {} items".format(pos, end))
	sys.stdout.flush()




if __name__ == "__main__":

	# connect to the database...
	db = DB(DB_HOST, DB_USERNAME, DB_PASSWORD, DB_DATABASE)

	# get all the args.
	args = sys.argv

	# running without args. Default is to get the list of proxies and add to the database.
	if len(args) == 1:

		getListProxies()
	
		processCurrent = None

		currentProxies = db.getExistingProxies()
		currentDeletedProxies = db.getDeletedProxies()

		file = open(FILE_PROXIES, 'r')
		urls = []

		for url in file:
			urls.append(url.strip())

		file.close()	
		
		print('STARTING TO BENCHMARK PROXIES...\n')

		proxies = []
		
		posProcessed = 1

	
		urls = (set(urls) - currentProxies) - currentDeletedProxies
	
		posEnd = len(urls) 
	
		for url in urls:
			# strip string
			url = url.strip()
			# if already is in database or ip is valid.
			if url in currentProxies or len(url) < 5:
				continue
			# get speed.
			urlSpeed = benchMarkUrl(url)

			# if speed is valid.
			if urlSpeed != None:
				proxies.append( {'url' : url, 'speed': urlSpeed} )

			# update items.
			if processCurrent != None and processCurrent.is_alive():
				processCurrent.join()
			else:
				processCurrent = Process(target=loadingItems, args=(posProcessed,posEnd,))
				processCurrent.start()
			posProcessed += 1

		# insert into the database...
		db.insertIntoTable(proxies)

		if processCurrent != None and processCurrent.is_alive():
			processCurrent.join()		
		print('\nFINISHED TO BENCHMARK PROXIES...')

	# you can update all proxies speeds and also exclude if the tested proxies are slowert than said speed.
	elif args[1] == 'update':

		limitSpeed = None
		hasSpeed = False

		# has a speed limit.
		if len(args) == 3 and args[2].find('speed=') != -1:
			hasSpeed = True
			limitSpeed = float(args[2][args[2].find('=') + 1:])

		# get existing proxies.
		currentProxies = db.getExistingProxies()
		
		processCurrent = None
		
		posProcessed = 1
	
		posEnd = len(currentProxies) 

		print("Updating proxies from your database...")

		proxiesDeleted = 0
		
		# go though each of them.
		for url in currentProxies:
			# get speed.
			urlSpeed = benchMarkUrl(url)
			# if speed is valid.
			if urlSpeed != None:
				# speed limit is set and current url is slower... remove it from the db.
				if hasSpeed and urlSpeed > limitSpeed:
					db.deleteProxy(url)
					proxiesDeleted += 1
				else:
					db.updateProxy(url, urlSpeed)
			else:
				db.deleteProxy(url)
				proxiesDeleted += 1

			# update items.
			if processCurrent != None and processCurrent.is_alive():
				processCurrent.join()
			else:
				processCurrent = Process(target=loadingItems, args=(posProcessed,posEnd,))
				processCurrent.start()
			posProcessed += 1


		if processCurrent != None and processCurrent.is_alive():
			processCurrent.join()		
		print('\nFinished the update...!')

		print('{} proxies were updated...'.format(posEnd - proxiesDeleted))
		print('{} proxies were deleted...'.format(proxiesDeleted))

	# delete all the slower proxies.
	elif len(args) == 3 and args[1] == 'delete' and args[2].find('speed=') != -1:
		
		limitSpeed = float(args[2][args[2].find('=') + 1:])

		proxiesList = db.getSpeedEqualOrHigher(limitSpeed)
	
		print('Deleting proxies slower than {} seconds...'.format(limitSpeed))
		for url in proxiesList:
			db.deleteProxy(url)
		print('Finished deleting proxies...')
