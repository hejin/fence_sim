#!/usr/bin/python

#####
##
##  APC Simulator with VirtualBox toolkit
##
##  Host        VirtualBox version
## +---------------------------------------------+
##  Windows 7   4.3.12r93733
##
#####

import sys, os, re, pexpect, exceptions
import traceback

import zmq
import time

sys.path.append("/home/roobot/src/fence_sim/")
from fencing import *

#BEGIN_VERSION_GENERATION
RELEASE_VERSION="1.0.2"
BUILD_DATE="(built Wed July 30 07:52:12 UTC 2014)"
GALAXYIO_COPYRIGHT="Copyright (C) GalaxyIO Technologies Co., Ltd. 2013-2014 All rights reserved."
#END_VERSION_GENERATION

class apc_vbox_conn():

    def start(self, ipaddr, port):
        try:
	    self.ctxt = zmq.Context()
	    self.sock = self.ctxt.socket(zmq.REQ)
            self.sock.connect("tcp://" + ipaddr + ":" + port);
        except Exception, ex:
            syslog.syslog(syslog.LOG_NOTICE, str(ex))
            pass

    def stop(self):
            self.ctxt.destroy()

def fence_login2(options):
        try:
            conn = apc_vbox_conn()
            conn.start(options["--ip"], options["--ipport"]);
	    #s.send(target_box + ' ' + fence_ops, copy=True)
            syslog.syslog(syslog.LOG_INFO, "APC Simulator login.")
            return conn
        except Exception, ex:
            syslog.syslog(syslog.LOG_NOTICE, str(ex))
            pass

def fence_logout(conn):
       try:
            conn.stop()
            syslog.syslog(syslog.LOG_INFO, "APC Simulator logout.")
       except Exception, ex:
            syslog.syslog(syslog.LOG_NOTICE, str(ex))
            pass

def get_power_status(conn, options):
            return "on"            

def set_power_status(conn, options):
        return

def fence_action2(tn, options, set_power_fn, get_power_fn, get_outlet_list = None):
        result = 0

	try:
		## Process options that manipulate fencing device
		#####
		if (options["--action"] == "list"):
			## @todo: exception?
			## This is just temporal solution, we will remove default value
			## None as soon as all existing agent will support this operation 
			print "NOTICE: List option is not working on this device yet"
			return

		status = get_power_status(tn, options)
		if status != "on" and status != "off":  
			fail(EC_STATUS)

		if options["--action"] == "on":
			if status == "on":
				print "Success: Already ON"
			else:
				power_on = False
				for _ in range(1, 1 + int(options["--retry-on"])):
					set_multi_power_fn(tn, options, set_power_fn)
					time.sleep(int(options["--power-wait"]))
					if wait_power_status(tn, options, get_power_fn):
						power_on = True
						break

				if power_on:
					print "Success: Powered ON"
				else:
					fail(EC_WAITING_ON)
		elif options["--action"] == "off":
			if status == "off":
				print "Success: Already OFF"
			else:
				set_multi_power_fn(tn, options, set_power_fn)
				time.sleep(int(options["--power-wait"]))
				if wait_power_status(tn, options, get_power_fn):
					print "Success: Powered OFF"
				else:
					fail(EC_WAITING_OFF)
		elif options["--action"] == "reboot":
                        syslog.syslog(syslog.LOG_INFO, "action: reboot")
                        print("Success: Rebooted")
                        return result
			if status != "off":
				options["--action"] = "off"
				set_multi_power_fn(tn, options, set_power_fn)
				time.sleep(int(options["--power-wait"]))
				if wait_power_status(tn, options, get_power_fn) == 0:
					fail(EC_WAITING_OFF)
			options["--action"] = "on"

			power_on = False
			try:
				for _ in range(1, 1 + int(options["--retry-on"])):
					set_multi_power_fn(tn, options, set_power_fn)
					time.sleep(int(options["--power-wait"]))
					if wait_power_status(tn, options, get_power_fn) == 1:
						power_on = True
						break
			except Exception, ex:
				# an error occured during power ON phase in reboot
				# fence action was completed succesfully even in that case
				sys.stderr.write(str(ex))
				syslog.syslog(syslog.LOG_NOTICE, str(ex))
				pass

			if power_on == False:
				# this should not fail as node was fenced succesfully
				sys.stderr.write('Timed out waiting to power ON\n')
				syslog.syslog(syslog.LOG_NOTICE, "Timed out waiting to power ON")

			print "Success: Rebooted"
		elif options["--action"] == "status":
			print "Status: " + status.upper()
			if status.upper() == "OFF":
				result = 2
		elif options["--action"] == "monitor":
			pass
	except pexpect.EOF:
		fail(EC_CONNECTION_LOST)
	except pexpect.TIMEOUT:
		fail(EC_TIMED_OUT)
	except pycurl.error, ex:
		sys.stderr.write(ex[1] + "\n")
		syslog.syslog(syslog.LOG_ERR, ex[1])
		fail(EC_TIMED_OUT)
	
	return result

#########################################################################

def main():
	device_opt = [  "ipaddr", "cmd_prompt", "port", "no_login", "no_password" ]

	atexit.register(atexit_handler)

	options = check_input(device_opt, process_input(device_opt))
	docs = { }
	docs["shortdesc"] = "Fence agent for VBox APC Simulator over telnet"
	docs["longdesc"] = "fence_apc_vbox is an I/O Fencing agent\
which can be used with the VBox APC APU simulator. It logs into device \
via telnet and reboots a specified outlet. Lengthy telnet connections \
should be avoided while a GFS cluster  is  running  because  the  connection \
will block any necessary fencing actions."
	docs["vendorurl"] = "http://www.galaxyio.com"
	show_docs(options, docs)
	conn = fence_login2(options)
        syslog.syslog(syslog.LOG_INFO, "login done")
        fence_logout(conn)
	result = -1
	result = fence_action2(conn, options, set_power_status, get_power_status, get_power_status)
	sys.exit(result)


if __name__ == "__main__":
	main()
