# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
from Queue import Queue
from threading import Thread
from splinter import Browser
from datetime import datetime
import time
import re

state='MN'

filename = 'results_%s.csv'%(datetime.now().strftime("%Y-%m-%d"))
bad_addresses = filename+'_bad_addresses'

f = open(filename,'w')
f.write("Street, City, State, Zip, Speed,emm_lat, emm_lng, emm_acc\n")
f.close()

e = open(bad_addresses,'w')
e.close()

def test2(address, emm_stuff):
    address_tmp = address.split(',')
    address = "%s, %s, %s, %s"%(address_tmp[0],address_tmp[1],state,address_tmp[2])
    try_again = True
    loop_count = 0
    while (try_again and loop_count < 3):
        loop_count = loop_count + 1
        try:
            browser = Browser('phantomjs')
            browser.driver.set_window_size(640,480)
            browser.visit('http://www.centurylink.com/')
            browser.find_by_id('landingRes').first.click()
            browser.find_by_id('home-speed-check').first.click()
            browser.find_by_id('ctam_new-customer-link').first.click()
            browser.is_text_present('Please enter your service address so we can show you accurate pricing product availability in your area', wait_time=5)
            browser.fill('form.singleLineAddress', address)
            browser.is_element_present_by_css('.ui-autocomplete.ui-menu.ui-widget.ui-widget-content.ui-corner-all', 15)
            addressFound = browser.find_by_css('.ui-autocomplete.ui-menu.ui-widget.ui-widget-content.ui-corner-all li a').first.text
            browser.find_by_css('.ui-autocomplete.ui-menu.ui-widget.ui-widget-content.ui-corner-all li a').first.click()

            addressFound_formatted = re.sub(r'%s (\d+)'%(state), r'%s,\1'%(state), addressFound)
            addressFound_formatted = re.sub(',USA', '', addressFound_formatted)
            while not browser.is_text_present('Choose an Offer'):
                time.sleep(1)
            try:
                element = browser.find_by_css('.highestSpeed')
            except:
                element = browser.find_by_css('.dialupOnly')
            extracted_speed_match = re.search("(\d+\.?\d?)",element.text)
            output = re.sub('\s+',' ', addressFound_formatted+', '+extracted_speed_match.group(0))
            print output
            f = open(filename,'a')
            f.write(output+",%s,%s,%s\n"%(emm_stuff[0], emm_stuff[1],emm_stuff[2]))
            browser.quit()
            try_again=False
            f.close()
        except:
            browser.quit()
            test2(address, emm_stuff)
    try:
        browser.quit()
    except:
        pass

def run_test(i):
    i = i.strip()
    street = i.split(',')[0]
    city = i.split(',')[1]
    zip = i.split(',')[2]
    emm_stuff = i.split(',')[-3:]
    test2(i, emm_stuff)

def do_stuff(q):
    while True:
        try:
            run_test(q.get())
            q.task_done()
        except:
            pass

q = Queue(maxsize=0)
num_threads = 30

for i in range(num_threads):
    worker = Thread(target=do_stuff, args=(q,))
    worker.setDaemon(True)
    worker.start()

houses = open('addresses','r')

for x in houses.readlines():
    q.put(x)

q.join()
