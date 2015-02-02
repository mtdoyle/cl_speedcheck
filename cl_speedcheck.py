from Queue import Queue
from threading import Thread
from splinter import Browser
from datetime import datetime
import re

state='MN'

filename = 'results_'+datetime.now().strftime("%Y-%m-%d")

f = open(filename,'w')
f.write("Street, City, State, Zip, Speed\n")
f.close()

e = open(filename+'_bad_addresses','w')
e.close()

def test(street, city, zip):
    try:
	f = open(filename,'a')
        browser = Browser()
        browser.visit('https://shop.centurylink.com/MasterWebPortal/freeRange/login/shop')
        browser.fill('form.streetAddress1', street)
        browser.fill('form.city', city)
        browser.select('form.addressState', state)
        browser.fill('form.addresszip', zip)
        browser.find_by_id('submitAuthAddress').first.click()
        browser.is_text_present('Choose an Offer', wait_time=5)
        try:
            element = browser.find_by_css('.highestSpeed')
        except:
            element = browser.find_by_css('.dialupOnly')
        extracted_speed_match = re.search("(\d+\.?\d?)",element.text)
        output = re.sub('\s+',' ', street+', '+city+', '+state+','+zip+', '+extracted_speed_match.group(0))
        print output 
        f.write(output+"\n")
        browser.quit()
	f.close()
    except:
        e = open('bad_addresses','a')
        e.write(street+', '+city+', '+state+', '+zip+'\n')
        e.close()
        browser.quit()

def run_test(i):
    i = i.strip()
    street = i.split(',')[0]
    city = i.split(',')[1]
    zip = i.split(',')[2]
    test(street, city, zip)

def do_stuff(q):
    while True:
        run_test(q.get())
        q.task_done()

q = Queue(maxsize=0)
num_threads = 15

for i in range(num_threads):
    worker = Thread(target=do_stuff, args=(q,))
    worker.setDaemon(True)
    worker.start()


houses = open('addresses','r')

for x in houses.readlines():
    q.put(x)

q.join()
