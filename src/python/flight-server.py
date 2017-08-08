#!flask/bin/python

import os
import time
import datetime
from subprocess import Popen
from threading import Thread, Event, Lock
from ConfigParser import RawConfigParser
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
from flight_xml import FlightXML, FlightXmlResult

class AdsbManager(Thread):
    def __init__(self):
        self._fifo = '/var/run/user/1000/FB_FIFO'
        self._kill = Event()
        self._planes = {}
        Thread.__init__(self)

    def kill(self):
        self._kill.set()

    def _process(self, line):
        d = line.split(' ')
        if len(d) == 5:
            key = d[0]
            if not self._planes.has_key(key):
                print 'New Flight: %s' % flight 
                flight = d[3]
                self._planes[key] = {'flight':flight, 'altitude':None}

        elif len(d) == 7:
            try:
                x = self._planes[key]
            except:
                return
            alt = int(d[5])
            if alt > 10000:
                print 'too high (%d ft)' % alt
                return

            lat = d[3]
            lon = d[4]

            print '%s: lat=%s, lon=%s, alt=%d ft' % (lat, lon, alt)
            x['lat'] = lat
            x['lon'] = lon
            x['altitude'] = alt
            x['grounded'] = int(d[6])
            x['timestamp'] = datetime.datetime.now()

    def run(self):
        cmd =  ['adsb_basestation']
        cmd += [self._fifo]
        p = Popen(cmd)

        with open(self._fifo) as fifo:
            while not self._kill.is_set():
                data = fifo.readline()
                if len(data) == 0:
                    self.kill()
                self._process(data)
        p.kill()

#TODO: MUTEX LOCKS!!
class FlightManager(Thread):
    def __init__(self):
        self._airport = 'KIAD'
        self._fxml = FlightXML('skramace', 'be7f0c874a5d1629dd9021b56d6cb31cd05feedb')
        self._departures = []
        self._arrivals = []

        self._lock = Lock()

        self._last_update = None
        self._last_raw_data = None 

        Thread.__init__(self)

    def _update_data(self):
        raw_data = self._fxml.load('/home/mjs/dev/plane-solari/src/python/IAD-query-201707290023.pickle')
        #raw_data = self._fxml.get_schedule(self._airport)
        self._last_raw_data = raw_data
        d = FlightXmlResult.get_sched(raw_data)

        self._lock.acquire()
        new_dep = []
        for dd in d:
            n = {
                'airline': dd.airline,
                'flightnumber': dd.flightnumber,
                'dcity': dd.destination['city'],
                'dtime': dd.estimated_departure_time['time'],
                'status': dd.status
            }
            new_dep.append(n)

        self._departures = new_dep
        self._lock.release()

    def run(self):
        #adsb = AdsbManager()
        #adsb.start()

        self._update_data()
        while 1:
            #track_flights()
            time.sleep(1)

    def get_arrivals(self):
        pass

    def get_departures(self):
        self._lock.acquire()
        ret = self._departures
        self._lock.release()
        return ret

class FlightBoardServer(Flask):
    def __init__(self, *args, **kwargs):
        self.fm = FlightManager()
        self.fm.start()
        super(FlightBoardServer, self).__init__(*args, **kwargs)

app = FlightBoardServer(__name__)
CORS(app)

@app.route('/planesolari/api/v1.0/flights', methods=['GET'])
def get_flights():
    fm = app.fm
    d = fm.get_departures()
    return jsonify({'departures': d})

@app.route('/')
def index():
    return 'Hello,World\nHola\nMundo'

if __name__ == '__main__':
    app.run(debug=True)
