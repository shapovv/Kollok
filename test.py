from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields, ValidationError
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)


class Flight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flight_number = db.Column(db.String(10), unique=True)
    departure = db.Column(db.String(50))
    destination = db.Column(db.String(50))
    departure_time = db.Column(db.DateTime)
    arrival_time = db.Column(db.DateTime)

    def serialize(self):
        return {
            'id': self.id,
            'flight_number': self.flight_number,
            'departure': self.departure,
            'destination': self.destination,
            'departure_time': self.departure_time,
            'arrival_time': self.arrival_time
        }


class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flight_id = db.Column(db.Integer, db.ForeignKey('flight.id'))
    passenger_id = db.Column(db.Integer)

    def serialize(self):
        return {
            'id': self.id,
            'flight_id': self.flight_id,
            'passenger_id': self.passenger_id
        }


class TicketSchema(Schema):
    flight_id = fields.Int(required=True)
    passenger_id = fields.Int(required=True)


@app.route('/flights', methods=['GET'])
def get_flights():
    flights = Flight.query.all()
    return jsonify([flight.serialize() for flight in flights])


@app.route('/tickets', methods=['POST'])
def buy_ticket():
    schema = TicketSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        abort(400, str(err))

    new_ticket = Ticket(**data)
    db.session.add(new_ticket)
    db.session.commit()

    return jsonify({'message': 'Ticket bought successfully'}), 201


@app.route('/tickets/<int:passenger_id>', methods=['GET'])
def get_tickets(passenger_id):
    tickets = Ticket.query.filter_by(passenger_id=passenger_id).all()
    return jsonify([ticket.serialize() for ticket in tickets])


@app.route('/tickets/<int:ticket_id>', methods=['DELETE'])
def cancel_ticket(ticket_id):
    ticket = Ticket.query.get(ticket_id)
    if ticket is None:
        abort(404, 'Ticket not found')

    db.session.delete(ticket)
    db.session.commit()
    return jsonify({'message': 'Ticket cancelled successfully'}), 200


@app.before_request
def create_tables():
    db.create_all()


# @app.before_request
# def create_tables_and_dummy_data():
#     db.create_all()
#
#     departure_time1 = datetime.strptime('2023-06-18 10:00:00', '%Y-%m-%d %H:%M:%S')
#     arrival_time1 = datetime.strptime('2023-06-18 12:30:00', '%Y-%m-%d %H:%M:%S')
#
#     departure_time2 = datetime.strptime('2023-06-18 15:00:00', '%Y-%m-%d %H:%M:%S')
#     arrival_time2 = datetime.strptime('2023-06-18 17:30:00', '%Y-%m-%d %H:%M:%S')
#
#     flight1 = Flight(flight_number='FN1234', departure='Samara', destination='Moscow', departure_time=departure_time1,
#                      arrival_time=arrival_time1)
#     flight2 = Flight(flight_number='FN5678', departure='Moscow', destination='Sochi', departure_time=departure_time2,
#                      arrival_time=arrival_time2)
#
#     db.session.add(flight1)
#     db.session.add(flight2)
#
#     db.session.commit()


if __name__ == '__main__':
    app.run(debug=True)
