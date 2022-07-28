#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 28 15:10:48 2022

@author: jp
"""

import cv2
import paramiko
from scp import SCPClient
import os
import time
import socket


def createSSHClient(server, port, user, password):
    
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password)
    return client


def setup():
    
    savepath = r'C:\Users\Lattice\Pictures\expmonitor\zeeman2\z2.png'
    cam = cv2.VideoCapture(0)
    ssh = createSSHClient('10.117.53.37', '22', 'admin', '3Helium4')
    scp = SCPClient(ssh.get_transport())
    
    return savepath, cam, scp


def iteration(savepath, cam, scp):
    
    result, image = cam.read()
    
    if result:
    
        print('Picture taken.')
        save_result = cv2.imwrite(savepath, image)
        if save_result: print('Picture saved.')
        scp.put(savepath, '/mnt/data/webcam/zeeman2')
        print('Picture sent.')
        os.remove(savepath)
        
        
if __name__ == '__main__':
    
    savepath, cam, scp = setup()
    while True:
        try:
            iteration(savepath, cam, scp)
        except (paramiko.buffered_pipe.PipeTimeout, socket.timeout, scp.SCPException):
            continue
        time.sleep(5)
