# Test WiFi 
#
# Usage:
# python test_wifi <wifi name> 
#
# How it works?
# This script tests for N things:
# 1. Bandwidth: Every 5 minutes the script starts downloading a big file
# It records the average bandwidth during the first 20 seconds of transfer.
# 2. Latency: The script pings the google dns server every 5 seconds. It records the latency and calculates jitter

import atexit
import argparse
import urllib2
import time
import datetime
import subprocess
from time import sleep
from threading import Thread

url = "http://download.thinkbroadband.com/10MB.zip"
file_url = 'http://download.thinkbroadband.com/1GB.zip'
file_url2 = 'ftp://ftp1.optonline.net/test64'
ping_ip = '8.8.8.8'

thread_latency = 0
thread_bandwidth = 0

def shutdown():
    print 'Not defined'

def test_bandwidth(shop_name):

    file_name = 'out_bw_' + shop_name
    out_bw_file = open(file_name, 'wb')

    out_bw_file.write('Test at ' + shop_name + ' : ' + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    out_bw_file.write("\n")

    # every 5 minutes
    # download file and record average bandwidth
    # during 20 seconds
    while True:
        file_name = file_url.split('/')[-1]

        headers = { 'User-Agent' : 'Mozilla/5.0' }
        req = urllib2.Request(file_url2, None, headers)
        u = urllib2.urlopen(req)

        file_metadata = u.info()
        file_size = int(file_metadata.getheaders("Content-Length")[0])

        file_size_dl = 0
        block_sz = 8192 * 16

        t0 = time.time()
        t1 = 0

        while True:
            buffer = u.read(block_sz)
            if not buffer:
               break

            file_size_dl += len(buffer)

            t1 = time.time()
            if t1 - t0 > 10: # 10seconds completed
                break

        out_bw_file.write(r"Bandwidth = %lf MB/s at %s" % ((file_size_dl / (t1-t0) / 1024.0 / 1024.0), str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))))
        out_bw_file.write("\n")
        out_bw_file.flush()

        # wait 1 minute
        sleep(60)


def test_latency(shop_name):
    out_lat_file = open('out_lat_' + shop_name, 'a+')
    
    while True:
        out_lat_file.write('Test at ' + shop_name + ' : ' + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        out_lat_file.write("\n")
        out_lat_file.flush()
        subprocess.call(['ping','-t','5',ping_ip], stdout=out_lat_file, stderr=subprocess.STDOUT)
        sleep(5) # 5 seconds


# ----------------------
#         MAIN
# ----------------------

if __name__ == "__main__":

    atexit.register(shutdown)

    parser = argparse.ArgumentParser(description='Test WiFi internet connection')
    parser.add_argument('shop_name', nargs=1, help='the WiFi network name')

    args = parser.parse_args()

    if not args.shop_name:
        print 'Coffee shop name missing'
        exit(-1)

    print '> ================================================================================'
    print '> Test WiFi utility ' + args.shop_name[0]
    print '> ================================================================================'
    print '>'

    thread_latency = Thread(target = test_latency, args = (args.shop_name[0],))
    thread_bandwidth = Thread(target = test_bandwidth, args = (args.shop_name[0],))

    thread_bandwidth.daemon = True
    thread_latency.daemon = True

    thread_latency.start()
    thread_bandwidth.start()

    while True:
        sleep(10)


