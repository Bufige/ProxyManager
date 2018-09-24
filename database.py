import mysql.connector


"""
You must have the database "proxies".
"""



##
## @brief      Class for database connection
##
class DB:

	##
	## @brief      Constructs the object.
	##
	## @param      self      The object
	## @param      host      The host
	## @param      user      The user
	## @param      password  The password
	## @param      database  The database
	##
	def __init__(self, host, user, password, database):
		self.db = mysql.connector.connect(
			host=host,
			user=user,
			passwd=password,
			database =database)
		self.cursor = self.db.cursor()

		self.createTables()
	
	##
	## @brief      Creates the default table
	##
	## @param      self  The object
	##
	##
	def createTables(self):		
		self.cursor.execute("CREATE TABLE IF NOT EXISTS working(ip VARCHAR(32) PRIMARY KEY UNIQUE, speed VARCHAR(64))")
		self.cursor.execute("CREATE TABLE IF NOT EXISTS deleted(ip VARCHAR(32) PRIMARY KEY UNIQUE)")
	##
	## @brief      insert the proxies into the database.
	##
	## @param      self     The object
	## @param      proxies  The proxies
	##
	##
	def insertIntoTable(self, proxies):
		sql = "INSERT INTO working(ip, speed) VALUES (%s, %s)"
		for item in proxies:
			val = [item['url'], item['speed']]
			try:
				self.cursor.execute(sql, val)
				self.db.commit()
			except Exception as e:
				self.db.rollback()

	##
	## @brief      Gets the existing proxies from the database
	##
	## @param      self  The object
	##
	## @return     The existing proxies.
	##
	def getExistingProxies(self):

		proxies = None
		try:
			self.cursor.execute("SELECT ip FROM working")

			proxies = self.cursor.fetchall()
		except:
			pass

		tmp = []
		for item in proxies:
			tmp.append(item[0])
		return set(tmp)		


	##
	## @brief      Gets the deleted proxies.
	##
	## @param      self  The object
	##
	## @return     The deleted proxies.
	##
	def getDeletedProxies(self):
		proxies = None

		try:
			self.cursor.execute("SELECT ip FROM deleted")

			proxies = self.cursor.fetchall()
		except:
			pass

		tmp = []
		for item in proxies:
			tmp.append(item[0])
		return set(tmp)

	##
	## @brief      update the proxy info.
	##
	## @param      self   The object
	## @param      ip     The ip
	## @param      speed  The speed
	##
	##
	def updateProxy(self, ip, speed):
		sql = "UPDATE working SET speed = %s WHERE ip = %s"
		val = (speed, ip, )
		try:
			self.cursor.execute(sql,val)
			self.db.commit()	
		except:	
			self.db.rollback()

	##
	## @brief      delete a proxy
	##
	## @param      self  The object
	## @param      ip    The ip
	##
	##
	def deleteProxy(self, ip):
		sql = "DELETE FROM working WHERE ip = %s"		
		sql2 = "INSERT INTO deleted(ip) VALUES (%s)"
		val = (ip,)
		try:
			self.cursor.execute(sql, val)
			self.cursor.execute(sql2, val)
			self.db.commit()
		except:
			self.db.rollback()
		

	##
	## @brief      Gets the speed equal or higher.
	##
	## @param      self   The object
	## @param      speed  The speed
	##
	## @return     A list of ips that are slower than the given speed.
	##
	def getSpeedEqualOrHigher(self, speed):
		sql = "SELECT ip FROM working WHERE speed >= %s"

		val = (speed,)

		proxies = None
		try:
			self.cursor.execute(sql,val)

			proxies = self.cursor.fetchall()
		except:
			pass

		tmp = []
		for item in proxies:
			tmp.append(item[0])
		return set(tmp)
