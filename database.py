import mysql.connector
from datetime import datetime


"""
You must have the database "proxies".
"""

from config import DEBUG, DB_HOST, DB_USERNAME, DB_PASSWORD, DB_DATABASE

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
	def __init__(self):
		self.db = mysql.connector.connect(
			host=DB_HOST,
			user=DB_USERNAME,
			passwd=DB_PASSWORD,
			database =DB_DATABASE)
		self.cursor = self.db.cursor()

		self.tableWorking = 'working'
		self.tableDeleted = 'deleted'

		self.createTables()
	
	##
	## @brief      Creates the default table
	##
	## @param      self  The object
	##
	##
	def createTables(self):		
		self.cursor.execute("CREATE TABLE IF NOT EXISTS {}(ip VARCHAR(32) PRIMARY KEY UNIQUE, speed VARCHAR(64), last_updated DATE NOT NULL)".format(self.tableWorking))
		self.cursor.execute("CREATE TABLE IF NOT EXISTS {}(ip VARCHAR(32) PRIMARY KEY UNIQUE)".format(self.tableDeleted))
	##
	## @brief      insert the proxies into the database.
	##
	## @param      self     The object
	## @param      proxies  The proxies
	##
	##
	def insertIntoTable(self, proxies):
		now = datetime.now()
		formatted_date = now.strftime('%d-%m-%Y %H:%M:%S')
		a = datetime.strptime(formatted_date, "%d-%m-%Y %H:%M:%S")

		sql = "INSERT INTO {}(ip, speed,last_updated) VALUES (%s, %s, %s)".format(self.tableWorking)
		for item in proxies:
			val = [item, proxies[item], a.strftime('%Y-%m-%d %H:%M:%S'),]
			try:
				self.cursor.execute(sql, val)
				self.db.commit()
			except Exception as e:
				if DEBUG:
					print("[ERROR]: Cannot insert into table =>" + str(e) )
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
			self.cursor.execute("SELECT ip FROM {}".format(self.tableWorking))

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
			self.cursor.execute("SELECT ip FROM {}".format(self.tableDeleted))

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
		now = datetime.now()
		formatted_date = now.strftime('%d-%m-%Y %H:%M:%S')
		a = datetime.strptime(formatted_date, "%d-%m-%Y %H:%M:%S")

		sql = "UPDATE {} SET speed = %s, last_updated = %s WHERE ip = %s".format(self.tableWorking)
		val = (speed, a.strftime('%Y-%m-%d %H:%M:%S'), ip, )
		try:
			self.cursor.execute(sql,val)
			self.db.commit()	
		except:	
			if DEBUG:
					print("[ERROR]: Cannot update table =>" + str(e) )
			self.db.rollback()

	##
	## @brief      delete a proxy
	##
	## @param      self  The object
	## @param      ip    The ip
	##
	##
	def deleteProxy(self, ip):
		sql = "DELETE FROM {} WHERE ip = %s".format(self.tableWorking)	
		sql2 = "INSERT INTO {}(ip) VALUES (%s)".format(self.tableDeleted)
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
		sql = "SELECT ip FROM {} WHERE speed >= %s".format(self.tableWorking)

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
