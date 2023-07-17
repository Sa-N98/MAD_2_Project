from flask_restful import Resource,reqparse
from application.model import *

user_args = reqparse.RequestParser()

user_args.add_argument("USER", type=str, required=True)
user_args.add_argument("movieID", type=str, required=True)
user_args.add_argument("venueID", type=str, required=True)
user_args.add_argument("dateID", type=str, required=True)
user_args.add_argument("NO_tickets", type=int, required=True)

class show_booking(Resource):
    def put(self):
        args = user_args.parse_args()
        show = Show_Venue.query.filter_by(s_id=args['movieID'],
                                          v_id=args['venueID'], 
                                          d_id=args['dateID']).first()
        show.seats = show.seats - args['NO_tickets']
        db.session.commit()
        return {'status':'Successfully update',
                'User':args['USER'],
                'movie-id':args['movieID'],
                'venue-id':args['venueID'],
                'date-id':args['dateID']
                }

    def post(self):
        args = user_args.parse_args()
        booking = booked_shows(user_name=args['USER'],
                               movieID=args['movieID'],
                               dateID=args['dateID'],
                               venueID=args['venueID'],
                               NO_tickets=args['NO_tickets']
                               )
        db.session.add(booking)
        db.session.commit()
        response = {
            'status': 'success',
            'message': 'Booking created successfully',
            'booking': {
                        'bookingID': booking.id,
                        'userID': booking.user_name,
                        'MovieID': booking.movieID,
                        'No-tickets': booking.NO_tickets
                        }
        }
        return response, 200




cancel_args = reqparse.RequestParser()
cancel_args.add_argument("NO_tickets", type=int, required=True)
cancel_args.add_argument("movieID", type=int, required=True)
cancel_args.add_argument("venueID", type=int, required=True)
cancel_args.add_argument("dateID", type=int, required=True)
cancel_args.add_argument("bookingID", type=int, required=True)


class show_cancel(Resource):
    def put(self):
        args = cancel_args.parse_args()
        show_ = Show_Venue.query.filter_by(s_id=args['movieID'], 
                                           v_id=args['venueID'], 
                                           d_id=args['dateID']).first()
        
        show_.seats = show_.seats + args['NO_tickets']
        db.session.commit()
        return "Successfully cancelled"
    
    def delete(self,bookind_id):
        print(bookind_id)
        booking = booked_shows.query.filter_by(id=bookind_id).first()
        db.session.delete(booking)
        db.session.commit()
        return {'status':'deleated'}