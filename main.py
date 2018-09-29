import sys
from manager import Manager


if __name__ == "__main__":

	manager = Manager()
	args = sys.argv

	# running without args. Default is to get the list of proxies and add to the database.
	if len(args) == 1:
		manager.add()
		
	# you can update all proxies speeds and also exclude if the tested proxies are slower than said speed.
	elif args[1] == 'update':
		
		limitSpeed = None
		hasSpeed = False

		# has a speed limit.
		if len(args) == 3 and args[2].find('speed=') != -1:
			hasSpeed = True
			limitSpeed = float(args[2][args[2].find('=') + 1:])

		manager.update(limitSpeed)
		

	# delete all the slower proxies based on the speed in seconds...
	elif len(args) == 3 and args[1] == 'delete' and args[2].find('speed=') != -1:
		limitSpeed = float(args[2][args[2].find('=') + 1:])
		manager.delete(limitSpeed)
	# will retry to add all the seen proxies so far.
	elif args[1] == 'retry':
		manager.reTry()