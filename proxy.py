import requests



##
## @brief      Class to handle request to websites with proxies.
##
class Proxy:

	##
	## @brief      Constructs the object.
	##
	## @param      self  The object
	## @param      url   The url
	## @param      ip    The ip of the proxy with the port.
	##
	def __init__(self, url, ip):
		self.url = url
		self.proxy = {'https' : ip}
		self.run()

	##
	## @brief      run the proxy.
	##
	## @param      self  The object
	##
	## @return     True if could make the connection , otherwise False.
	##
	def run(self):
		status = True
		try:
			req = requests.get(self.url, proxies = self.proxy)
		except:
			status = False
		return status