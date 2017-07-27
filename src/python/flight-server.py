#!flask/bin/python
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)

# Test Data
arrivals = [
    {
        'carrier':'ASA',
        'flight' :'729',
        'tofrom' :'Seatle',
        'status' :'In Air',
        'sched'  :'11:00',
        'gate'   :'B71'
    },
    {
        'carrier':'MJS',
        'flight' :'2222',
        'tofrom' :'Rome',
        'time'   :'22:30',
        'gate'   :'M22'
    }
]

departures = [
    {
        'carrier':'UAL',
        'flight' :'861',
        'tofrom' :'Sao Paulo',
        'status' :'Delayed',
        'sched'  :'13:00',
        'gate'   :'C12'
    }
]

@app.route('/planesolari/api/v1.0/flights', methods=['GET'])
def get_flights():
    return jsonify({'arrivals': arrivals, 'departures': departures})

@app.route('/')
def index():
    return 'Hello,World\nHola\nMundo'

if __name__ == '__main__':
    app.run(debug=True)
