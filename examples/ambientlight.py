#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`gyroscope`
==================

Created by hbldh <henrik.blidh@nedomkull.com>
Created on 2016-04-26

"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import time

from pymetawear.client import discover_devices, MetaWearClient, libmetawear

print("Discovering nearby MetaWear boards...")
metawear_devices = discover_devices(timeout=2)
if len(metawear_devices) < 1:
    raise ValueError("No MetaWear boards could be detected.")
else:
    address = metawear_devices[0][0]

c = MetaWearClient(str(address), 'pygatt', debug=True)
print("New client created: {0}".format(c))


def callback(data):
    """Handle ambient light notification callback."""
    print("Ambient Light: {0}".format(data))


print("Write ambient light settings...")
c.ambient_light.set_settings(gain=4, integration_time=200, measurement_rate=200)
print("Subscribing to ambient light signal notifications...")
c.ambient_light.notifications(callback)

time.sleep(20.0)

print("Unsubscribe to notification...")
c.ambient_light.notifications(None)

time.sleep(5.0)

c.disconnect()