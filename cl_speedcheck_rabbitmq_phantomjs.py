# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import pika
import os
from Queue import Queue
from threading import Thread
from datetime import datetime
import time
import re
from selenium import webdriver

state='MN'

filename = 'results_%s.csv'%(datetime.now().strftime("%Y-%m-%d"))

count = 1
while os.path.isfile(filename):
    filename = 'results_%s_%s.csv'%(datetime.now().strftime("%Y-%m-%d"), count)
    count = count + 1


if not os.path.isfile(filename):
    f = open(filename,'w')
    f.write("Street, City, State, Zip, Speed,emm_lat, emm_lng, emm_acc\n")
    f.close()

def test3(address, emm_stuff):
    try:
        address_tmp = address.split(',')
        address = "%s, %s, %s, %s"%(address_tmp[0],address_tmp[1],state,address_tmp[2])
        service_args = [
            '--proxy=localhost:3128',
            '--load-images=false',
        ]
        dcap = {}
        dcap["phantomjs.page.settings.userAgent"] = (
             "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A"
        )
        browser = webdriver.PhantomJS('/usr/bin/phantomjs', service_args=service_args,desired_capabilities=dcap)
        browser.set_window_size(640,480)
        browser.get('http://www.centurylink.com/')
        try:
            browser.find_element_by_id('landingRes').click()
        except:
            pass
        browser.find_element_by_id('home-speed-check').click()
        browser.find_element_by_id('ctam_new-customer-link').click()
        browser.find_element_by_id('ctam_nc-sfaddress').send_keys(address)
        browser.find_element_by_css_selector('.ui-autocomplete.ui-menu.ui-widget.ui-widget-content.ui-corner-all')
        time.sleep(2)
        addressFound = browser.find_element_by_css_selector('li.ui-menu-item:nth-child(1) > a:nth-child(1)').text
        print addressFound
        browser.find_element_by_css_selector('li.ui-menu-item:nth-child(1) > a:nth-child(1)').click()
        try:
            browser.find_element_by_id('ctam_nc-go').click()
        except:
            pass

        addressFound_formatted = re.sub(r'%s (\d+)'%(state), r'%s,\1'%(state), addressFound)
        addressFound_formatted = re.sub(',USA', '', addressFound_formatted)
        count = 0
        while not 'Choose an Offer' in browser.page_source and count < 10:
            if 'We need some additional information' in browser.page_source:
                browser.find_element_by_id('addressid2').click()
                browser.find_element_by_id('submitSecUnit').click()
            time.sleep(1)
            count = count + 1
        try:
            element = browser.find_element_by_css_selector('.highestSpeed')
        except:
            element = browser.find_element_by_css_selector('.dialupOnly')
        extracted_speed_match = re.search("(\d+\.?\d?)",element.text)
        if extracted_speed_match != "866":
            output = re.sub('\s+',' ', addressFound_formatted+', '+extracted_speed_match.group(0))
            f = open(filename,'a')
            f.write(output+",%s,%s,%s\n"%(emm_stuff[0], emm_stuff[1],emm_stuff[2]))
            f.close()
        browser.quit()
    except:
        pass

def run_test(i):
    i = i.strip()
    emm_stuff = i.split(',')[-3:]
    test3(i, emm_stuff)

def callback(ch, method, properties, body):
    run_test('%s'%(body,))
    ch.basic_ack(delivery_tag = method.delivery_tag)

def do_stuff(q):
    while True:
        connection = pika.BlockingConnection(pika.ConnectionParameters(
                host='localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='clspeed')
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(callback,
                      queue='clspeed',
                      )
        channel.start_consuming()
        q.task_done()

q = Queue(maxsize=0)
num_threads = 30

for i in range(num_threads):
    worker = Thread(target=do_stuff, args=(q,))
    #worker.setDaemon(True)
    worker.start()

q.join()
