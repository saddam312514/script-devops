# ## For  logging
import logging
import random
import datetime

from locust import HttpUser, task



user_logins = [("01711091125", "12345678"),
               ("01711091126", "12345678"),
               ("01711091127", "12345678"),
               ("01711091128", "12345678"),
               ("01711091129", "12345678")]

bus_types = {"AC_B": 1, "AC_S": 2, "SNIGDHA": 3, "F_BERTH": 4, "F_SEAT": 5,
             "F_CHAIR": 6, "S_CHAIR": 7, "SHOVAN": 8, "SHULOV": 9, "AC_CHAIR": 10}

bus_types_list = ["AC_B", "AC_S", "SNIGDHA", "F_BERTH", "F_SEAT",
                  "F_CHAIR", "S_CHAIR", "SHOVAN", "SHULOV", "AC_CHAIR"]




routes = [("Dhaka","Chattogram"), ("Chattogram","Dhaka"), ("Dhaka","Rangpur"), ("Dhaka","Rajshahi"), ("Dhaka","Dinajpur"), ("Dhaka","Jashore")]


# from http.client import HTTPConnection

# HTTPConnection.debuglevel = 1
# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True

logger = logging.getLogger()

def get_search_id(response):
    for line in response.splitlines(): 
        # line = line.strip() #or some other preprocessing
        search_id = None
        if (line.find('www-search-id"') != -1):
            index = line.find("value")
            search_id = line[index+7:]
            search_id = search_id[:-3]
            return search_id

class TrainSearchUser(HttpUser):
    @task
    def search_user_flow(self):
        # Login to get session cookie
        #user_detail = random.choice(user_logins)
        seat_class = random.choice(bus_types_list)
        seat_class = 'S_CHAIR'
        travel_date = datetime.datetime.now(
        ) + datetime.timedelta(days=random.sample(range(5), 1)[0])
        travel_date_str = travel_date.strftime("%d-%b-%Y")

        route = random.choice(routes)
        from_city = route[0]
        to_city = route[1]

        #from_city = "Dhaka"
        #to_city = "Dinajpur"

        # Access the home page
        response = self.client.get("/")
        #logger.info("Access homepage status : " + str(response.status_code))

        # Perform search
        response = self.client.get("/booking/train/search?fromcity=" + from_city +
                                   "&tocity=" + to_city + "&doj=" + travel_date_str + "&class="+seat_class, name="Search Tickets")

        if response.status_code != 200:
            return

        search_id = get_search_id(response.text)
        logger.info("search_id is : " + search_id)

        # Get Trains
        response = self.client.get('/booking/train/search/results/0/' +
                                   search_id + '?seat_type=' + str(bus_types.get(seat_class)), name="Get Trains")
        
        logger.info(response.status_code)
