fence_toy
=========

a simple fence toolkit using pyzmq to work around the virtualbox vm status bug in Windows host

Howto:
1. running the server in Windows host with the same user account who launched the VirtualBox VMs
2. launch the fence request in a VirtualBox VM to forcedly start/poweroff/reboot another VM

N.B. 
1. In the host side, the path to the VBoxManage utilit is hardcoded in fence_daemon.py
2. In the client side, the host IP is hardcoded in fence_req.py
