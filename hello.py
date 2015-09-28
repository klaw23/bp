import json
import os
import re
import requests

from bs4 import BeautifulSoup
from flask import Flask, request

app = Flask(__name__)
app.debug = True

@app.route('/')
def hello():
    # Use a requests session to log in.
    with requests.Session() as s:
        # Get the CSRF token.
        response = s.get('https://postmates.com')
        soup = BeautifulSoup(response.text)
        csrf_token = soup.findAll(attrs={"name":"csrf-token"})[0]['content']

        # Login.
        response = s.post('https://postmates.com/v1/web_login'
                          '?client=customer.web&version=0.0.0',
                          data={'username': request.args['username'],
                                'password': request.args['password']},
                          headers={'Referer': 'https://postmates.com',
                                   'X-CSRFToken': csrf_token})

        # Get the CSRF token.
        response = s.get('https://postmates.com')
        soup = BeautifulSoup(response.text)
        csrf_token = soup.findAll(attrs={"name":"csrf-token"})[0]['content']

        # Add burrito to cart.
        response = \
        s.post('https://postmates.com/v1/carts/'
               'a17da034-8f9f-48a8-bab5-25759c6a01ec'
               '/add?client=customer.web&version=0.0.0',
               data={'product_uuid': 'e666416e-6d59-4f90-a5d4-9f64868f9e7b',
                     'quantity': 1,
                     'option_uuids': '8cb6c855-f3a5-4fad-ac3e-1270042d19e7,'
                         '964e4afa-c3c3-47d6-87a0-a4765163cb3c,'
                         'e9ceac76-252d-460b-8b74-632f8e5b4473,'
                         'c1649357-29b9-4db8-98e9-f8f0467d6de8',
                     'special_instructions': ''},
               headers={'Referer': 'https://postmates.com/sf/'
                        'pancho-villa-taqueria-san-francisco/view/'
                        'e666416e-6d59-4f90-a5d4-9f64868f9e7b',
                        'X-CSRFToken': csrf_token})

        # Get CSRF token and checkout data.
        response = s.get('https://postmates.com/sf/'
                         'pancho-villa-taqueria-san-francisco/checkout')
        soup = BeautifulSoup(response.text)
        csrf_token = soup.findAll(attrs={"name":"csrf-token"})[0]['content']
        pickup = soup.findAll(attrs={"name":"pickup_place_uuid"})[0]['value']
        cart_id = soup.findAll(attrs={"name":"cart_uuid"})[0]['value']
        cart_generation = soup.findAll(attrs={"name":"cart_generation"})[0]['value']
        # TODO(kevin): Use a specific address.
        dropoff = soup.find(id='form-select-address').findAll('option')[1]['value']

        # Fetch credit card info in a separate json request.
        # TODO(kevin): Use a specific card.
        card = json.loads(s.get('https://postmates.com/v1/cards'
                                '?client=customer.web&version=0.0.0')
                          .text)['cards'][0]['uuid']

        # Place order.
        response = \
        s.post('https://postmates.com/v1/jobs'
               '?client=customer.web&version=0.0.0',
               data={'pickup_place_uuid': pickup,
                     'cart_uuid': cart_id,
                     'cart_generation': cart_generation,
                     'dropoff_address_uuid': dropoff,
                     'card_uuid': card},
               headers={'Referer': 'https://postmates.com/sf/'
                        'pancho-villa-taqueria-san-francisco/checkout',
                        'X-CSRFToken': csrf_token})

        # Get the job id.
        job_id = json.loads(response.text)['uuid']

        # Submit the job.
        response = \
        s.post('https://postmates.com/v1/jobs/%s/fsm_update'
               '?client=customer.web&version=0.0.0' % job_id,
               data={'action': 'DoDispatchRequest'},
               headers={'Referer': 'https://postmates.com/sf/'
                        'pancho-villa-taqueria-san-francisco/checkout',
                        'X-CSRFToken': csrf_token})

    return response.text

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
