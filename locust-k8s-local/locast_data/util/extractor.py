from bs4 import BeautifulSoup
import json


def get_confirmation_url(response):
    index1 = response.find('http')
    # print(index1)
    if (index1 != -1):
        line = response[index1:]
        index2 = response.find(";")
        # print(index2)
        return response[index1:index2-1]

def get_booking_id(url):
    from urllib.parse import urlparse, parse_qs
    parse_result = urlparse(url)
    dict_result = parse_qs(parse_result.query)
    return dict_result['booking_id'][0]

def get_order_id(response):
    for line in response.splitlines(): 
        # line = line.strip() #or some other preprocessing
        order_id = None
        index = line.find("var orderId = '")
        if (index != -1):
            order_id = line[index+15:]
            order_id = order_id[:-2]
            return order_id

### Web app utils

def find_available_trains(soup):

    train_seat_classes = []
    # get the container
    rows = soup.findAll('div',
                        attrs={'class': 'row single-trip-wrapper list_rows'})

    if (len(rows) > 0):
        for row in rows:
            train_seats_available = row.findAll('div',
                                                attrs={'class': 'single-seat-class'})

            if (len(train_seats_available) > 0):
                for train_seat in train_seats_available:
                    train_seat_classes.append(json.loads(
                        train_seat.get('data-seat-type')))

    return train_seat_classes


def find_all_avaiable_seats(soup):
    return_data = {"train_seats": [], "boarding_points": []}

    # get the container
    rows = soup.findAll('li', {"data-seat": True})

    if (len(rows) > 0):
        for row in rows:
            seat_data = json.loads(row.get('data-seat'))
            if seat_data['seatAvailable'] == 1:
                return_data["train_seats"].append(seat_data)

    for option in soup.select('select[id=boardingpoint] > option'):
        return_data["boarding_points"].append(option['value'])

    return return_data


def get_payment_form_submit_data(soup, no_passengers=1):

    body = {'contactperson': 0,
            'pmobile': None,
            'pemail': None,
            'insurance': 'insurance_no',
            'selected_mobile_transaction': 1,
            'bkash-online': 'bkash-online',
            'search_id': None,
            'www_search_id': 0,
            'pay_type': 2,
            'priyojon_order_id': None
            }
    
    name = soup.findAll('input', attrs={"id" :"pname"})[0].get('value')
    body['pmobile'] = str(soup.select('input[id=pmobile]')[0].get('value'))
    body['pemail'] = str(soup.select('input[id=pemail]')[0].get('value'))
    
    append_str = " abcd"

    # body['passengerType[]'] = "Adult"*no_passengers
    # body['gender[]'] = "male"*  no_passengers

    for i in range(no_passengers):
        body['pname['+ str(i) + ']']  =  (name + append_str[i]).strip()
        body['gender['+ str(i) + ']'] = 'male'
        body['passengerType['+ str(i) + ']'] = "Adult"
        body['page['+ str(i) + ']'] = None
        body['ppassport['+ str(i) + ']'] = None
    
    return body

####  PWA Utils

def find_all_avaiable_pwa_seats(response):
    train_seats = []

    if (len(response) > 0):
        for floor in response:
            layout = floor["layout"]
            for  each_set in layout:
                for  seat in each_set:
                    if seat['seat_availability'] == 1:
                        train_seats.append(seat)

    return train_seats

def prepare_booking_request(frm, to, doj, seat_class, trip_id, trip_route_id, boarding_point_id, name, mobile, email, tickets):
    payload = {
        "from_city": frm,
        "to_city": to,
        "date_of_journey": doj,
        "seat_class": seat_class,
        "trip_id": int(trip_id),
        "trip_route_id": int(trip_route_id),
        "boarding_point_id": boarding_point_id,
        "pmobile": mobile,
        "pemail": email,
        "contactperson": 0,
        "selected_mobile_transaction": 1,
        "is_bkash_online": 1
    }

    append_str = " abcd"
    for i, ticket in enumerate(tickets):
        payload['ticket_ids['+ str(i) + ']']= ticket["ticket_id"]
        payload['pname['+ str(i) + ']']  =  (name + append_str[i]).strip()
        payload['gender['+ str(i) + ']'] = 'male'
        payload['passengerType['+ str(i) + ']'] = "Adult"
 
    return payload

def get_search_id(response):
    for line in response: 
        # line = line.strip() #or some other preprocessing
        search_id = None
        #print(line)
        if (line.find('www-search-id"') != -1):
            index = line.find("value")
            search_id = line[index+7:]
            search_id = search_id[:-3]
            return search_id




if __name__ == '__main__':
    # soup = BeautifulSoup(open("test/resources/search.html"), 'html.parser')
    # seat_type = "F_SEAT"
    # seats = find_available_trains(soup)

    # type_seats = [seat for seat in seats if seat['type'] == seat_type]
    # print(json.dumps(type_seats, indent=2))

    # soup = BeautifulSoup(open("test/resources/boarding.html"), 'html.parser')
    # print(json.dumps(find_all_avaiable_seats(soup), indent=2))

    # soup = BeautifulSoup(open("test/resources/paymentform.html"), 'html.parser')
    # print(json.dumps(get_payment_form_submit_data(soup, 2), indent=2))

    # search_id = get_search_id(open("searchpage.html"))
    # print(search_id)

    order_id = get_order_id(open("test.html"))
    print(order_id)

# trip_available = {"key": 5, "type": "F_SEAT", "trip_id": 543709, "trip_route_id": 2420375,
#                   "route_id": 3107, "fare": "1500.00", "vat_percent": 15, "seat_counts": {"online": 6, "offline": 6}}


# dataseat={"ticket_id":28758797,"trip_id":541829,"company_id":137,"seat_number":"KA-4","seat_column":5,"seat_row":1,"seat_floor":0,"ticket_type":1,"ticket_status":1,"seat_type_id":1,"fare_type_id":1,"is_selected_for_booking":1,"counter_id":null,"floor_name":"KA","fare_type_name":"Economy","seatAvailable":1}
