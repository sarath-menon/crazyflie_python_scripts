"""
Simple example that connects to the first Crazyflie found, logs the Stabilizer
and prints it to the console. After 10s the application disconnects and exits.
"""
import logging
import time
from threading import Timer

import cflib.crtp  # noqa
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.utils import uri_helper

import numpy as np
import csv

# uri = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')
uri = uri_helper.uri_from_env(default='usb://0')

# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)


class LoggingExample:
    """
    Simple logging example class that logs the Stabilizer from a supplied
    link uri and disconnects after 5s.
    """

    def __init__(self, link_uri):
        """ Initialize and run the example with the specified link_uri """

        self._cf = Crazyflie(rw_cache='./cache')

        # Connect some callbacks from the Crazyflie API
        self._cf.connected.add_callback(self._connected)
        self._cf.disconnected.add_callback(self._disconnected)
        self._cf.connection_failed.add_callback(self._connection_failed)
        self._cf.connection_lost.add_callback(self._connection_lost)

        print('Connecting to %s' % link_uri)

        # Try to connect to the Crazyflie
        self._cf.open_link(link_uri)

        # Variable used to keep main loop occupied until disconnect
        self.is_connected = True

        # open the file in the write mode
        self.csv_file = open('./logging/logs/gyro/log_1.csv', 'w')

        # create the csv writer
        self.writer = csv.writer(self.csv_file)

        header = ['timestamp', 'gyro_unfiltered.x', 'gyro_unfiltered.y', 'gyro_unfiltered.z',  'gyro_filtered.x', 'gyro_filtered.y', 'gyro_filtered.z']
        # write the header
        self.writer.writerow(header)
        

    def _connected(self, link_uri):
        """ This callback is called form the Crazyflie API when a Crazyflie
        has been connected and the TOCs have been downloaded."""
        print('Connected to %s' % link_uri)

        # The definition of the logconfig can be made before connecting
        self._lg_stab = LogConfig(name='Stabilizer', period_in_ms=100)
        self._lg_stab.add_variable('gyro.x', 'float')
        self._lg_stab.add_variable('gyro.y', 'float')
        self._lg_stab.add_variable('gyro.z', 'float')


        self._lg_stab.add_variable('gyro_unfiltered.x', 'float')
        self._lg_stab.add_variable('gyro_unfiltered.y', 'float')
        self._lg_stab.add_variable('gyro_unfiltered.z', 'float')

        # The fetch-as argument can be set to FP16 to save space in the log packet
        self._lg_stab.add_variable('pm.vbat', 'FP16')

        # Adding the configuration cannot be done until a Crazyflie is
        # connected, since we need to check that the variables we
        # would like to log are in the TOC.
        try:
            self._cf.log.add_config(self._lg_stab)
            # This callback will receive the data
            self._lg_stab.data_received_cb.add_callback(self._stab_log_data)
            # This callback will be called on errors
            self._lg_stab.error_cb.add_callback(self._stab_log_error)
            # Start the logging
            self._lg_stab.start()
        except KeyError as e:
            print('Could not start log configuration,'
                  '{} not found in TOC'.format(str(e)))
        except AttributeError:
            print('Could not add Stabilizer log config, bad configuration.')

        # Start a timer to disconnect in 10s
        t = Timer(5, self._cf.close_link)
        t.start()

    def _stab_log_error(self, logconf, msg):
        """Callback from the log API when an error occurs"""
        print('Error when logging %s: %s' % (logconf.name, msg))

    def _stab_log_data(self, timestamp, data, logconf):
        """Callback from a the log API when data arrives"""
        print(f'[{timestamp}][{logconf.name}]: ', end='')
        
        gyro_filtered = np.array([data["gyro.x"], data["gyro.y"], data["gyro.z"]])
        gyro_unfiltered = np.array([data["gyro_unfiltered.x"], data["gyro_unfiltered.y"], data["gyro_unfiltered.z"]])

        print(f"Gyro filtered: {gyro_filtered[0]:3.3f} {gyro_filtered[1]:3.3f} {gyro_filtered[2]:3.3f}", end='')

        data = [timestamp, gyro_unfiltered[0], gyro_unfiltered[1], gyro_unfiltered[2],  gyro_filtered[0], gyro_filtered[1], gyro_filtered[2]]

        # write data to csvile f
        self.writer.writerow(data)
        
        print()

    def _connection_failed(self, link_uri, msg):
        """Callback when connection initial connection fails (i.e no Crazyflie
        at the specified address)"""
        print('Connection to %s failed: %s' % (link_uri, msg))
        self.is_connected = False

    def _connection_lost(self, link_uri, msg):
        """Callback when disconnected after a connection has been made (i.e
        Crazyflie moves out of range)"""
        print('Connection to %s lost: %s' % (link_uri, msg))

    def _disconnected(self, link_uri):
        """Callback when the Crazyflie is disconnected (called in all cases)"""
        print('Disconnected from %s' % link_uri)
        self.is_connected = False


if __name__ == '__main__':
    # Initialize the low-level drivers
    cflib.crtp.init_drivers()

    le = LoggingExample(uri)

    # The Crazyflie lib doesn't contain anything to keep the application alive,
    # so this is where your application should do something. In our case we
    # are just waiting until we are disconnected.
    while le.is_connected:
        time.sleep(1)
