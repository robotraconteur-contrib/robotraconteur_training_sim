from RobotRaconteur.Client import *
import time

def autodiscover(service_type,name):
	time.sleep(2)

	res=RRN.FindServiceByType(service_type,["rr+local","rr+tcp","rrs+tcp"])
	for serviceinfo2 in res:
		if name in serviceinfo2.Name:
			return serviceinfo2.ConnectionURL[0]
			
	return 