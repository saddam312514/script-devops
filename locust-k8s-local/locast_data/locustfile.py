# ## For  logging
import logging
import random
import json
import datetime

from bs4 import BeautifulSoup
from locust import HttpUser, task

import extractor
import inputdata

from http.client import HTTPConnection

# HTTPConnection.debuglevel = 1
# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True

logger = logging.getLogger()

class TrainLoginUser(HttpUser):
    @task
    def logged_in_user_flow(self):
        # Login to get session cookie
        user_detail = random.choice(inputdata.user_logins)
        seat_class = random.choice(inputdata.bus_types_list)
        #seat_class = 'S_CHAIR'
        travel_date = datetime.datetime.now(
        ) + datetime.timedelta(days=random.sample(range(5), 1)[0])
        travel_date_str = travel_date.strftime("%d-%b-%Y")

        logger.info("user detail is : " + str(user_detail))
        logger.info("seat class is : " + seat_class)
        logger.info("travel date is : " + travel_date_str)

        route = random.choice(inputdata.routes)
        from_city = route[0]
        to_city = route[1]

        # from_city = "Dhaka"
        # to_city = "Dinajpur"

        # Login user
        response = self.client.post(
            "/auth/sign-in", json={"mobile_number": user_detail[0], "password": user_detail[1]}, name="Login user")
        # logger.info(response.text)

        # Perform search
        response = self.client.get("/booking/train/search?fromcity=" + from_city +
                                   "&tocity=" + to_city + "&doj=" + travel_date_str + "&class="+seat_class, name="Search Tickets")
        soup = BeautifulSoup(response.text, 'html.parser')
        search_id = soup.find(id='www-search-id').get('value')
        logger.info("search_id is : " + search_id)

        # Get Trains
        response = self.client.get('/booking/train/search/results/0/' +
                                   search_id + '?seat_type=' + str(inputdata.bus_types.get(seat_class)), name="Get Trains")
        soup = BeautifulSoup(response.text, 'html.parser')
        trains = extractor.find_available_trains(soup)
        # logger.info(json.dumps(trains, indent=2))
        type_seats = [seat for seat in trains if seat['type'] == seat_class]
        # logger.info(json.dumps(type_seats, indent=2))

        if (len(type_seats) == 0):
            logger.info("No trains available")
            response = self.client.post("/logout/en", name="Logout user")
            return

        type_seat = random.choice(type_seats)

        # Get Seat Counts
        response = self.client.get('/booking/train/search/seat-counts/' + str(
            type_seat['trip_id']) + '/' + str(type_seat['route_id']), name="Get seat counts")
        logger.info("search output is : " + response.text)

        # Get Seats
        response = self.client.post('/booking/trip/' + str(type_seat['trip_id']) + '/' + str(
            type_seat['trip_route_id']) + '/seat-selection/' + search_id, json={"trip": "onward"}, name="Get Seats")
        soup = BeautifulSoup(response.text, 'html.parser')
        # logger.info("search output is : " + response.text)
        seats_boardingpoints = extractor.find_all_avaiable_seats(soup)
        seats = seats_boardingpoints["train_seats"]
        boardingpoints = seats_boardingpoints["boarding_points"]
        # logger.info("dumping seats")
        # logger.info(json.dumps(seats, indent=2))

        if (len(seats) == 0):
            logger.info("No trains available")
            response = self.client.post("/logout/en", name="Logout user")
            return

        # select any number of seats between 1 to 4
        no_of_seats = random.sample(range(1, 5), 1)[0]
        seat_number = random.sample(range(len(seats)-4), 1)[0]

        selected_seats = []
        for i in range(no_of_seats):
            selected_seats.append(seats[seat_number+i])

        # Reserve them and release some of them, but keep a random number of them

        for seat in selected_seats:
            reserved_data = {"ticketid": seat["ticket_id"],
                             "routeid": type_seat['trip_route_id'],
                             "searchid": search_id}

            response = self.client.post(
                '/booking/train/seat/reserve', data=reserved_data, name="Reserve Seat")

            logger.info("reserve output is : " + response.text)

        # confirm booking
        boarding = random.choice(boardingpoints)
        confirm_data = {"boardingpoint": boarding,
                        "searchid": search_id}

        response = self.client.post(
            '/booking/train/confirm', data=confirm_data, name="Confirm Booking", allow_redirects=False)

        logger.info("confirm booking status : " + str(response.status_code))
        logger.info("confirm booking redirect url : " +
                    response.headers["location"])

        # Load the page and get the email and mobile number and name
        response = self.client.get(
            response.headers["location"], name="Load payment form")
        soup = BeautifulSoup(response.text, 'html.parser')

        # confirm payment
        request_data = extractor.get_payment_form_submit_data(
            soup, no_of_seats)
        request_data['search_id'] = search_id

        logger.info(request_data)
        import urllib
        request_data = urllib.parse.urlencode(request_data)
        request_headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            # 'Content-Type': 'application/json',
            'Accept':  'application/json'
        }
        response = self.client.post(
            '/booking/train/pay-now', data=request_data, name="Confirm Payment", headers=request_headers, allow_redirects=False)

        logger.info("confirm payment status : " + str(response.status_code))
        logger.info("confirm payment redirect url : " +
                    str(response.headers["location"]))
        # logger.info("reserve output is : " + response.text)

        request_headers = {
            # 'Content-Type': 'application/x-www-form-urlencoded',
            # 'Content-Type': 'application/json',
            'Accept':  '*/*'
        }
        response = self.client.get(
            response.headers["location"], name="Payment beta call", headers=request_headers, allow_redirects=False)

        logger.info("Payment beta call status : " + str(response.status_code))
        # logger.info("confirm payment1 redirect url : " +
        #            str(response.headers["location"]))
        logger.info("Payment beta call response is : " + response.text)

        confirmation_url  = extractor.get_confirmation_url(response.text)
        order_id = extractor.get_order_id(confirmation_url)

        response = self.client.get(
            confirmation_url, name="Confirmation Page", headers=request_headers, allow_redirects=False)

        logger.info("Confirmation Page status : " + str(response.status_code))
        logger.info("confirm payment1 redirect url : " +
                    str(response.headers["location"]))
        
        # logger.info("Confirmation Page  response is : " + response.text)

        ticket_url = response.headers["location"]

        response = self.client.get(
            response.headers["location"], name="Ticket Page", headers=request_headers, allow_redirects=False)

        logger.info("Ticket Page status : " + str(response.status_code))
        # logger.info("confirm payment1 redirect url : " +
        #            str(response.headers["location"]))
        #logger.info("Ticket Page  response is : " + response.text)
        #logger.info("Ticket Page  headers  : " + response.headers)

        request_headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            #'Content-Type': 'application/json',
            'Accept':  'application/json'
        }

        update_pdf_url = "/booking/update-pdf-download"
        body  = {
            "order_id" : order_id
        }
        response = self.client.post(
            update_pdf_url, name="Update Pdf download", headers=request_headers, data=body)

        logger.info("Update Pdf download status : " + str(response.status_code))
        logger.info("Update Pdf download response: " + response.text)

        referer = self.host + ticket_url

        # request_headers = {
        #     "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        #     "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        #     "cache-control": "max-age=0",
        #     "sec-ch-ua": "\"Not?A_Brand\";v=\"8\", \"Chromium\";v=\"108\", \"Google Chrome\";v=\"108\"",
        #     "sec-ch-ua-mobile": "?0",
        #     "sec-ch-ua-platform": "\"macOS\"",
        #     "sec-fetch-dest": "document",
        #     "sec-fetch-mode": "navigate",
        #     "sec-fetch-site": "same-origin",
        #     "upgrade-insecure-requests": "1",
        #     "Referer": referer,
        #     "Referrer-Policy": "strict-origin-when-cross-origin"
        #     #"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        # }
        response = self.client.get(
            referer, name="PDF Ticket Page") #, headers=request_headers)

        logger.info("Ticket Page status : " + str(response.status_code))
        # logger.info("confirm payment1 redirect url : " +
        #            str(response.headers["location"]))
        logger.info("Ticket Page  headers  : " )
        logger.info(response.headers)

        out = open(search_id[0:4] + ".pdf", 'w')

        out.write(response.text)
        out.close()

        # Logout
        response = self.client.post("/logout/en", name="Logout user")


# class TrainSearchUser(HttpUser):
#     @task
#     def search_user_flow(self):
#         # Login to get session cookie
#         user_detail = random.choice(inputdata.user_logins)
#         seat_class = random.choice(inputdata.bus_types_list)
#         seat_class = 'S_CHAIR'
#         travel_date = datetime.datetime.now(
#         ) + datetime.timedelta(days=random.sample(range(5), 1)[0])
#         travel_date_str = travel_date.strftime("%d-%b-%Y")

#         logger.info("user detail is : " + str(user_detail))
#         logger.info("seat class is : " + seat_class)
#         logger.info("travel date is : " + travel_date_str)

#         route = random.choice(inputdata.routes)
#         from_city = route[0]
#         to_city = route[1]

#         #from_city = "Dhaka"
#         #to_city = "Dinajpur"

#         # Access the home page
#         response = self.client.get("/")
#         logger.info("Access homepage status : " + str(response.status_code))

#         # Perform search
#         response = self.client.get("/booking/train/search?fromcity=" + from_city +
#                                    "&tocity=" + to_city + "&doj=" + travel_date_str + "&class="+seat_class, name="Search Tickets")
#         soup = BeautifulSoup(response.text, 'html.parser')
#         search_id = soup.find(id='www-search-id').get('value')
#         logger.info("search_id is : " + search_id)

#         # Get Trains
#         response = self.client.get('/booking/train/search/results/0/' +
#                                    search_id + '?seat_type=' + str(inputdata.bus_types.get(seat_class)), name="Get Trains")
#         soup = BeautifulSoup(response.text, 'html.parser')
#         trains = extractor.find_available_trains(soup)
#         # logger.info(json.dumps(trains, indent=2))
#         type_seats = [seat for seat in trains if seat['type'] == seat_class]
#         # logger.info(json.dumps(type_seats, indent=2))

#         if (len(type_seats) == 0):
#             logger.info("No trains available")
#             response = self.client.post("/logout/en", name="Logout user")
#             return
