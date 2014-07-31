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
	#result = fence_action(conn, options, set_power_status, get_power_status, get_power_status)
	sys.exit(result)


if __name__ == "__main__":
	main()
