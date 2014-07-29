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

# event queue between worker and dispatcher
q_evt= Queue.Queue()

class fence_evt:
	def __init__(self):
		self.fence_target = ''
		self.fence_ops	  = ''

	def get_fence_target(self):
		return self.fence_target

	def set_fence_target(self, fence_target):
		self.fence_target = fence_target

	def get_fence_ops(self):
		return self.fence_ops

	def set_fence_ops(self, fence_ops):
		self.fence_ops = fence_ops

# major thread for fence handle
def do_fence(fence_target, fence_ops):
	cmdpath = os.getcwd()
	oscmd = ['D:\\Program Files\Oracle\VirtualBox\VBoxManage.exe', 'controlvm', fence_target, fence_ops]
	pipe = Popen(oscmd, stdout = PIPE)
	rc = pipe.communicate()[0]
	# for debug
	print rc
	print "fence done."
	
def __fence_worker(evt):
	print "do evt handling ... " + evt.get_fence_target() + ' ' + evt.get_fence_ops()
	fence_ops 	 = evt.get_fence_ops()
	fence_target = evt.get_fence_target()
	
	do_fence(fence_target, fence_ops)

def fence_worker():
	print "fence worker started ..."	
	while True:
		e = q_evt.get()
		__fence_worker(e)


if __name__ == '__main__':

#	scan all IOC/HBAs, encloures and disks, build mapping between them

#	fork evt handler thread
	t_fence_worker = Thread(target = fence_worker)
	t_fence_worker.start()

#	setup socket server, and wait-for & handle coming fence evts
	c = zmq.Context()
	s = c.socket(zmq.REP)
	s.bind('tcp://*:5556')
	
	while True:
		msg = s.recv(copy=True)
		s.send(msg)
		str_msg = str(msg)
		print('fence request msg recvd : ' + str_msg)
		fence_target, fence_ops = str_msg.split()
		print 'target box: ' + fence_target
		print 'fence  ops: ' + fence_ops
		e = fence_evt()
		e.set_fence_target(fence_target)
		e.set_fence_ops(fence_ops)
		q_evt.put(e)

	
	t_fence_worker.join()
