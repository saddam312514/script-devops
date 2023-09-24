# ## For  logging
import logging
import random
import json
import datetime
import sys
import requests

from bs4 import BeautifulSoup
from json import JSONDecodeError

import sys
sys.path.append("..")
from util import extractor as extractor
from util import inputdata as inputdata

from http.client import HTTPConnection

# HTTPConnection.debuglevel = 1
# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger()

host_url = "https://pwaapi9.shohoz.com"


def signout(client, token):
    # post
    # /auth/sign-out
    request_headers = {
        'Authorization': "Bearer " + token,
        'Accept':  'application/json',
    }
    response = client.post(
        host_url + "/v1.0/app/auth/sign-out", headers=request_headers)
    logger.info("Logout status code:")
    logger.info(response.status_code)
    logger.info(response.json())


user_detail = random.choice(inputdata.user_logins)
seat_class = random.choice(inputdata.bus_types_list)
seat_class = 'S_CHAIR'
travel_date = datetime.datetime.now(
) + datetime.timedelta(days=random.sample(range(5), 1)[0])
travel_date_str = travel_date.strftime("%d-%b-%Y")

logger.info("user detail is : " + str(user_detail))
logger.info("seat class is : " + seat_class)
logger.info("travel date is : " + travel_date_str)

route = random.choice(inputdata.routes)
from_city = route[0]
to_city = route[1]

from_city = "Dhaka"
to_city = "Rajshahi"

request_headers = { 
    'Content-Type': 'application/json',
    'Accept':  'application/json'
}

# Login user
response = requests.post(
    host_url + "/v1.0/app/auth/sign-in", json={"mobile_number": user_detail[0], "password": user_detail[1]}, headers=request_headers)
logger.info("Login user status code:")
logger.info(response.status_code)
token = response.json()["data"]['token']
logger.info(token)

# All gets
# /auth/profile
request_headers = {
    'Accept':  'application/json',
    'Authorization': "Bearer " + token
}
response = requests.get(
    host_url + "/v1.0/app/auth/profile", headers=request_headers, allow_redirects=False)
logger.info("auth profile status code:")
logger.info(response.status_code)
# logger.info(response.headers)
profile = response.json()["data"]
logger.info(profile)

android_params = "android_app_version=4.3.6&android_device_id=eebf729d51489b2b"

# Perform search
request_headers = {
    'Accept':  'application/json',
    'Authorization': "Bearer " + token
}
url = host_url + "/v1.0/app/bookings/search-trips?from_city=" + from_city + "&to_city=" + to_city + \
"&date_of_journey=" + travel_date_str + \
        "&seat_class=" + seat_class + '&' + android_params
response = requests.get(
        url, headers=request_headers)
logger.info("search trips status code:")
logger.info(response.status_code)
# logger.info(response.headers)
search_trips_rsp = response.json()["data"]['trips']
# logger.info(json.dumps(search_trips_rsp))

if (len(search_trips_rsp["list"]) == 0):
    logger.info("No trains available")
    signout(requests, token)
    exit()

# select a train
train = random.choice(search_trips_rsp["list"])

trip_id = str(train["tripId"])
trip_route_id = str(train["tripRouteId"])
# Seat Layout
url = host_url + "/v1.0/app/bookings/seat-layout?trip_id=" + trip_id + \
    "&trip_route_id=" + trip_route_id + '&' + android_params
response = requests.get(
    url, headers=request_headers)
logger.info("seat layout status code:")
logger.info(response.status_code)
if response.status_code != 200:
    logger.info(response.json())
    signout(requests, token)
    exit()
tickets_rsp = response.json()["data"]['seatLayout']
# logger.info(tickets_rsp)

# Get Available Seats
seats = extractor.find_all_avaiable_pwa_seats(tickets_rsp)
# logger.info(seats)

if (len(seats) == 0):
    logger.info("No trains available")
    signout(requests, token)
    exit()

# patches
# select any number of seats between 1 to 4
no_of_seats = random.sample(range(1, 5), 1)[0]
#no_of_seats = 1
seat_number = 0
if no_of_seats < len(seats):
    seat_number = random.sample(range(len(seats)-4), 1)[0]
else:
    no_of_seats = len(seats)

selected_seats = []
for i in range(no_of_seats):
    selected_seats.append(seats[seat_number+i])

# Reserve them and release some of them, but keep a random number of them
request_headers = {
    'Content-Type': 'application/json',
    'Accept':  'application/json',
    'Authorization': "Bearer " + token
}
url = host_url +  "/v1.0/app/bookings/reserve-seat?" + android_params
for seat in selected_seats:
    reserved_data = {"ticket_id": str(seat["ticket_id"]),
                        "route_id": trip_route_id
                        }

    response = requests.patch(
        url, headers=request_headers, json=reserved_data)
    logger.info("reserve seat status code:")
    logger.info(response.status_code)
    reserved_seat_rsp = response.json()
    logger.info(reserved_seat_rsp)

# /bookings/release-seat
# /bookings/confirm\
boarding_point = random.choice(train["boardingPoints"])
confirm_data = extractor.prepare_booking_request(from_city, to_city, travel_date_str,
                                                    seat_class, trip_id, trip_route_id, boarding_point["trip_point_id"], profile['display_name'], profile['phone_number'], profile['email'], selected_seats)
request_headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    # 'Content-Type': 'application/json',
    'Accept':  'application/json',
    'Authorization': "Bearer " + token
}
url = host_url + "/v1.0/app/bookings/confirm?" + android_params
logger.info(confirm_data)
response = requests.patch(
    url, headers=request_headers, data=confirm_data)
logger.info("booking confirm status code:")
logger.info(response.status_code)
booking_rsp = response.json()
logger.info(booking_rsp)

response = requests.get(
    booking_rsp["data"]["redirectUrl"], headers=request_headers, data=confirm_data)
logger.info("pay shohoz status code:")
logger.info(response.status_code)
#booking_rsp = response.json()
logger.info(response.text)

confirmation_url = extractor.get_confirmation_url(response.text)

booking_id = extractor.get_booking_id(confirmation_url)

# /bookings/confirm-payment
confirm_paymennt_data = {
    "booking_id": booking_id,
    "trxid": None,
    "completed": None
}
request_headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    # 'Content-Type': 'application/json',
    'Accept':  'application/json',
    'Authorization': "Bearer " + token
}
url = host_url + "/v1.0/app/bookings/confirm-payment?" + android_params
response = requests.patch(
    url, headers=request_headers, data=confirm_paymennt_data)
logger.info("bookings/confirm-payment status code:")
logger.info(response.status_code)
#booking_rsp = response.json()
pnr = response.json()["data"]["orders"][0]["pnr"]
ticket_url = response.json()["data"]["orders"][0]["ticket_url"]
logger.info("PNR is : " + pnr)
logger.info("ticket  url is : " + ticket_url)

# post
# /auth/sign-out
signout(requests, token)
