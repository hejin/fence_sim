#!/bin/env python

import zmq
import time
import sys

if __name__ == '__main__':

	if len(sys.argv) != 3:
		print('Usage: ' + sys.argv[0] + ' SPA|SPB reboot|poweroff|poweron')
		exit(1)
	target_box = sys.argv[1]
	fence_ops  = sys.argv[2]
	c = zmq.Context()
	s = c.socket(zmq.REQ)
	s.connect('tcp://192.168.56.1:5556')
	s.send(target_box + ' ' + fence_ops, copy=True)
	print('Notified fence event :' + target_box + ' ' + fence_ops + ' done.')
