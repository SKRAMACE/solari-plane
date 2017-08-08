#!/usr/bin/env python

import requests
import cPickle as pickle

class FlightXML(object):
    baseurl = 'https://flightxml.flightaware.com/json/FlightXML3/'

    def __init__(self, username, key):
        self._username = username
        self._key = key

    def _get_auth(self):
        return (self._username, self._key)

    def get_schedule(self, airport, offset=0):
        url = self.baseurl + 'AirportBoards'
        payload = {'airport_code':airport, 'type':'all', 'filter':'airline', 'offset':offset}
        auth = self._get_auth()
        response = requests.get(url, params=payload, auth=auth)

        if response.status_code == 200:
            return response.json()
        else:
            return None

    def save(self, filename, data):
        with open(filename, 'w') as f:
            pickle.dump(data, f)
        
    def load(self, filename):
        with open(filename, 'r') as f:
            data = pickle.load(f)
        return data

class Flight(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def arrive_time(self):
        return '{dow} {date} {time}'.format(**self.estimated_arrival_time)

    def depart_time(self):
        return '{dow} {date} {time}'.format(**self.estimated_departure_time)

class FlightXmlResult(object):
    @staticmethod
    def _get_flight_data(data, key):
        print key
        return data['AirportBoardsResult'][key]['flights']

    @staticmethod
    def _get_airport_name(data):
        return data['AirportBoardsResult']['airport']['flights']

    @staticmethod
    def _get_flights(data):
        for d in data:
            print d
            print type(d)
        return map(lambda x: Flight(**x), data)

    @classmethod
    def _list_flights(cls, data, key):
        flight_list = cls._get_flight_data(data, key)
        flights = cls._get_flights(flight_list)
        for f in flights:
            flight = f.airline + f.flightnumber
            tail = getattr(f, 'tailnumber', '')

            if tail:
                flight += ' - %s' % tail 

            dcity = f.origin['city']
            dtime = f.depart_time()

            acity = f.destination['city']
            atime = f.arrive_time()

            print flight
            print '\tdeparts %s @ %s' % (dcity, dtime)
            print '\tarrives %s @ %s' % (acity, atime)
        print ''

    @classmethod
    def list_sched(cls, data):
        cls._list_flights(data, 'scheduled')

    @classmethod
    def list_enroute(cls, data):
        cls._list_flights(data, 'enroute')

    @classmethod
    def list_arrivals(cls, data):
        cls._list_flights(data, 'arrivals')

    @classmethod
    def list_departures(cls, data):
        cls._list_flights(data, 'departures')

    @classmethod
    def list_all(cls, data):
        cls.list_sched(data)
        cls.list_enroute(data)
        cls.list_arrivals(data)
        cls.list_departures(data)

    @classmethod
    def get_sched(cls, data):
        flight_list = cls._get_flight_data(data, 'scheduled')
        return cls._get_flights(flight_list)

    @classmethod
    def get_enroute(cls, data):
        flight_list = cls._get_flight_data(data, 'enroute')
        return cls._get_flights(flight_list)

    @classmethod
    def get_arrivals(cls, data):
        flight_list = cls._get_flight_data(data, 'arrivals')
        return cls._get_flights(flight_list)

    @classmethod
    def get_departures(cls, data):
        flight_list = cls._get_flight_data(data, 'departures')
        return cls._get_flights(flight_list)

if __name__ == '__main__':
    fxml = FlightXML('skramace', 'be7f0c874a5d1629dd9021b56d6cb31cd05feedb')
    data = fxml.load('offset0.dat')

    f = FlightXmlResult.get_enroute(data)
    for ff in f:
        print ff.__dict__
        print 'carrier: %s' % ff.airline
        print 'flight: %s' % ff.flightnumber
        print 'from: %s' % ff.origin['city']
        print 'sched: %s' % ff.arrive_time()
        print ''
