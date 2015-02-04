------address_generator.py-------

Requirements for address_generator.py:
  1. pygeocoder: https://pypi.python.org/pypi/pygeocoder

Generate a list of addresses with address_generator.py. Use a mapping website to find two addresses that would be the NW and SE boundaries of the "box" you want to generate addresses in. The script will produce a file called "addresses" which should be in the correct format for the input of cl_speedcheck.py. You can increase or decrease the amount of addresses generated by altering the values that the latitude and longitude are stepped by. There is a limit to the number of times you can reverse-geocode per day. I believe you can check up to 25,000 addresses, but I'm not positive. I have hit the limit before while debugging this script. If you are going to check a wide area, I'd strongly suggest increasing the stepping values. 

The script only allows generated addressed that start with a number and has no hyphens. I did this for simplicity sake since the speed checking script seemed to have problems processing them. I still get a healthy number of addresses when omitting these, but YMMV. 


------cl_speedcheck.py-------

Requirements for cl_speedcheck.py:
  1. A list of addresses generated by address_generator.py
    - formatted like this: \<street>,\<state>,\<zip>,\<lat>,\<lon>,ROOFTOP
    - one address per line
  2. splinter: https://splinter.readthedocs.org/en/latest/
  3. Firefox browser (not a hard requirement - it's the default browser that splinter uses and what my script uses)

This script could use some work. It opens 15 instances of Firefox and queries the CenturyLink website for the fastest available speed at each address. The number of instances opened can be alterd by changing the value of "num_threads". Sometimes the address checked is an apartment building and I believe the script just fails or crashes - but I catch the exception and basically ignore it so the script can keep running. I don't really use the "bad_addresses" output file since some of the address that can end up in there could be valid addresses but something just went wrong while the script ran.

The output of this script is a list of addresses that were successfully checked in this format:

    <street>, <city>, <state>, <zip>, <highest speed in Mbps>, <lat>, <lon>, ROOFTOP
  
If an address has gigabit available, it will show up as 1000.

To map these results, use a service such as http://www.easymapmaker.com. For easymapmaker.com, replace all commas in the results_* file with tabs. Then, you can simply copy+paste the file contents into easymapmaker.com and it'll process them. 

Happy checking!
