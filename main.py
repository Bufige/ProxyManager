import sys
import time
import datetime


from manager import Manager


HOUR_IN_SECONDS = 60*60

TIME_SCHEDULER = True

SCHEDULER_TIMING = {'add' : HOUR_IN_SECONDS, 'update' : HOUR_IN_SECONDS + HOUR_IN_SECONDS/2, 'retry' : HOUR_IN_SECONDS*1.80 + HOUR_IN_SECONDS/2}


def main():
	manager = Manager()

	if TIME_SCHEDULER:
		nextScheduler = None
		while True:
			if nextScheduler == None or nextScheduler < datetime.datetime.now():
				manager.add()
				manager.update()
				manager.reTry()
				nextScheduler = datetime.datetime.now() + datetime.timedelta(seconds=HOUR_IN_SECONDS)
				print('[{}]Finished current schedule...'.format(datetime.datetime.now()))
				print('next schedule is => [{}]'.format(nextScheduler))
		return None
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

if __name__ == "__main__":
	main()