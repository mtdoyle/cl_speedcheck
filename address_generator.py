from pygeocoder import Geocoder
from datetime import datetime
import time
import re

filename = 'addresses'

f = open(filename,'w')
f.close()

start_lat=
start_lon=

end_lat=
end_lon=

sleep_cycle=0

curr_lat = start_lat
curr_lon = start_lon

geocoder = Geocoder()

while curr_lon < end_lon or curr_lat > end_lat:
    try:
        results = geocoder.reverse_geocode(curr_lat, curr_lon)
        if re.search("^(\d+)$",str(results[0]).split()[0]) is not None:
            l = str(results[0]).split(',')
            addr = ("%s,%s,%s"%(l[0],l[1].strip(),l[2].split()[1]))
            print addr
            f = open(filename,'r+a')
            if addr not in f.read():
                addr = addr+",%s,%s,ROOFTOP"%(curr_lat, curr_lon)
                f.write(addr+"\n")
            f.close()
        if curr_lat > end_lat:
            curr_lat = curr_lat - .002
        else:
            curr_lat = start_lat
            curr_lon = curr_lon + .002
        sleep_cycle = sleep_cycle + 1
        if sleep_cycle == 4:
            time.sleep(1)
            sleep_cycle = 0
    except:
        continue

if __name__ == "__main__":
    

