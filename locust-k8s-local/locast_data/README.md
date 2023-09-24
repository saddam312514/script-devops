

Instructions
============

- Install python3 and pip
- Install locust and BeautifulSoup
    https://docs.locust.io/en/stable/installation.html
    https://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-beautiful-soup

- Clone the project and run 'locust' from command line and visit http://localhost:8089/# to execute the tests

Headless run:
--------------

WEB:

locust -u <user_count> -r <spawn_rate> -t <duration>  -f locustfiles/web.py --headless --print-stats --csv Run1.csv --csv-full-history  --host=https://trainbeta.shohoz.com

For all options, run 'locust -h' on command line

-----

Functional Tests
----------------

If you want to see the flow only once.

- cd functional
- python3  functional_<web,pwa>.py
