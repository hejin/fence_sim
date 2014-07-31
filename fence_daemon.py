#!/bin/env python
from threading import Thread

from subprocess import Popen, PIPE, call
import sys
import os
import zmq
import sys
import Queue
import urllib2
import json
import string
import time

def do_get_power_state(box):
	oscmd = ['D:\\Program Files\Oracle\VirtualBox\VBoxManage.exe', 'list', 'runningvms']
	pipe = Popen(oscmd, stdout = PIPE)
	running_vms_info = pipe.communicate()[0]
	# for debug
	#print running_vms_info
	## check if the box is running
	found = 0
	for line in running_vms_info.split(os.linesep):
		running_box = line.split(' ')
		if ("\""+ box + "\"" == running_box[0]):
			found = 1

	if (found == 0):
		print("controller " + box + " is not running")
		return "off"

	print("controller " + box + " is running")
	return "on"
	
def do_set_power_state(fence_ops, box):
	############################
	#if (fence_ops == "on" or fence_ops == "reboot"):
	#	return "on"
	
	#return "off"	
	############################

	vboxmgmt_path = 'D:\\Program Files\Oracle\VirtualBox\VBoxManage.exe'
	if (fence_ops == "on"):
		oscmd = [vboxmgmt_path, 'startvm', box, '--type', 'headless']
	else:
		oscmd = [vboxmgmt_path, 'controlvm', box, 'poweroff']	
	
	print oscmd
	pipe = Popen(oscmd, stdout = PIPE)
	rc = pipe.communicate()[0]
	# for debug
	print rc
	time.sleep(5)
	return do_get_power_state(box)


# major thread for fence handle
def do_fence(fence_ops, fence_plug):
	if (fence_plug == "1"):
		fence_target_box = "SPA"
	elif (fence_plug == "2"):
		fence_target_box = "SPB"
	else:
		sys.stderr.write("No valid controller attached to the plug #" + str(fence_plug))
		return

	# handle request
	if (fence_ops == "GetPowerState"):
		return do_get_power_state(fence_target_box)
	elif (fence_ops == "on" or fence_ops == "off"):
		return do_set_power_state(fence_ops, fence_target_box)
	else:	
		sys.stderr.write("Not a valid ops: " + str(fence_ops))

	return

class fence_worker():
	def __init__(self, bind_addr):
		self.bind_addr = bind_addr

	def setup(self):
		self.ctxt = zmq.Context()
		self.sock = self.ctxt.socket(zmq.REP)
		self.sock.bind(self.bind_addr)
		print("fence simulator started ...")

	def recv(self, copy=True):
		return self.sock.recv(copy=True)	

	def send(self, data):
		self.sock.send(data)	

if __name__ == '__main__':

	fence = fence_worker("tcp://*:5556")
	fence.setup()
	
	while True:
			msg = fence.recv(copy=True)
			str_msg = str(msg)
			print('fence request msg recvd : ' + str_msg)
			fence_ops, fence_plug = str_msg.split()
			print 'fence  ops:  ' + fence_ops
			print 'fence  plug: ' + fence_plug
			rc = do_fence(fence_ops, fence_plug)
			print rc
			fence.send(rc) 
