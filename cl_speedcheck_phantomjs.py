# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
from Queue import Queue
from threading import Thread
from datetime import datetime
import time
import re
from selenium import webdriver

state='MN'

filename = 'results_%s.csv'%(datetime.now().strftime("%Y-%m-%d"))
bad_addresses = filename+'_bad_addresses'

f = open(filename,'w')
f.write("Street, City, State, Zip, Speed,emm_lat, emm_lng, emm_acc\n")
f.close()

e = open(bad_addresses,'w')
e.close()

def test3(address, emm_stuff):
    address_tmp = address.split(',')
    address = "%s, %s, %s, %s"%(address_tmp[0],address_tmp[1],state,address_tmp[3])
    service_args = [
        '--proxy=localhost:3128',
    ]
    browser = webdriver.PhantomJS('/usr/bin/phantomjs', service_args=service_args)
    browser.set_window_size(640,480)
    browser.get('http://www.centurylink.com/')
    browser.find_element_by_id('landingRes').click()
    browser.find_element_by_id('home-speed-check').click()
    browser.find_element_by_id('ctam_new-customer-link').click()
    browser.find_element_by_id('ctam_nc-sfaddress').send_keys(address)
    browser.find_element_by_css_selector('.ui-autocomplete.ui-menu.ui-widget.ui-widget-content.ui-corner-all')
    time.sleep(2)
    addressFound = browser.find_element_by_css_selector('li.ui-menu-item:nth-child(1) > a:nth-child(1)').text
    print addressFound
    browser.find_element_by_css_selector('li.ui-menu-item:nth-child(1) > a:nth-child(1)').click()

    addressFound_formatted = re.sub(r'%s (\d+)'%(state), r'%s,\1'%(state), addressFound)
    addressFound_formatted = re.sub(',USA', '', addressFound_formatted)
    while not 'Choose an Offer' in browser.page_source:
        time.sleep(1)
    try:
        element = browser.find_element_by_css_selector('.highestSpeed')
    except:
        element = browser.find_element_by_css_selector('.dialupOnly')
    extracted_speed_match = re.search("(\d+\.?\d?)",element.text)
    output = re.sub('\s+',' ', addressFound_formatted+', '+extracted_speed_match.group(0))
    f = open(filename,'a')
    f.write(output+",%s,%s,%s\n"%(emm_stuff[0], emm_stuff[1],emm_stuff[2]))
    browser.quit()
    f.close()

def run_test(i):
    i = i.strip()
    emm_stuff = i.split(',')[-3:]
    test3(i, emm_stuff)

def do_stuff(q):
    while True:
        run_test(q.get())
        q.task_done()

q = Queue(maxsize=0)
num_threads = 50

for i in range(num_threads):
    worker = Thread(target=do_stuff, args=(q,))
    worker.setDaemon(True)
    worker.start()

houses = open('addresses','r')

for x in houses.readlines():
    q.put(x)

q.join()
