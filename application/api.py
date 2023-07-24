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
    


admin_args = reqparse.RequestParser()
admin_args.add_argument("theater", type=str)
admin_args.add_argument("place", type=str)
admin_args.add_argument("movie", type=str)
admin_args.add_argument("posterURL", type=str)
admin_args.add_argument("bannerURL", type=str)
admin_args.add_argument("date", type=str)
admin_args.add_argument("id", type=int)
admin_args.add_argument("rating", type=int)
admin_args.add_argument("seats", type=int)
admin_args.add_argument("price", type=int)


class venue_update(Resource):
    def post(self):
        args = admin_args.parse_args()
        new_venue = venue(name=args['theater'],
                          place=args['place']
                         )
        db.session.add(new_venue)
        db.session.commit()
        response = {
            'status': 'success',
            'message': 'venue created successfully',
            'booking': {
                        # 'VenueID': new_venue.id,
                        'Name': new_venue.name,
                        'Place': new_venue.place,
                        }
                    }
        return response, 200
    def put(self):
        args = admin_args.parse_args()
        theater = venue.query.filter_by(id=args['id']).first()
        if theater:
            theater.name = args['theater']
            theater.place = args['place']
            db.session.commit()
            return "Successfully Updated"
        return "Theater Not Found"
    
    def delete(self,venue_id):
        del_venue = venue.query.filter_by(id=venue_id).first()
        db.session.delete(del_venue)
        db.session.commit()
        del_show=Show_Venue.query.filter_by(v_id=venue_id).all()
        if Show_Venue:
            for item in del_show:
                db.session.delete(item)
                db.session.commit()

        return {'status':'deleated'}

class show_update(Resource):
    def post(self):
        args = admin_args.parse_args()
        if show.query.filter_by(name=args['movie']).first():
            new_show=show.query.filter_by(name=args['movie']).first()
        else:
            new_show = show(name=args['movie'],
                            poster=args['posterURL'],
                            posterLong=args['bannerURL'],
                            rating=args['rating']
                            )
            db.session.add(new_show)
            db.session.commit()

        new_date=date.query.filter_by(dates=args['date']).first()
        if not new_date:
            new_date=date(dates=args['date'])
            db.session.add(new_date)
            db.session.commit()
            
        new_show_venue=Show_Venue(s_id=new_show.id,
                                  v_id=venue.query.filter_by(name=args['place']).first().id,
                                  d_id=new_date.id,
                                  seats=args['seats'],
                                  price=args['price'],
                                  starting_seats=args['seats']
                                  )
        db.session.add(new_show_venue)
        db.session.commit()
        print( new_show_venue.s_id)
        response = {
            'status': 'success',
            'message': 'movie added'}
        return response, 200
    
       
    def put(self):
        args = admin_args.parse_args()
        theater = venue.query.filter_by(id=args['id']).first()
        if theater:
            theater.name = args['theater']
            theater.place = args['place']
            db.session.commit()
            return "Successfully Updated"
        return "Theater Not Found"
    
    def delete(self,sid,vid,did):
        print(sid,vid,did)
        del_show=Show_Venue.query.filter_by(s_id=sid,v_id=vid,d_id=did).all()
        print(del_show)
        if del_show:
            for item in del_show:
                db.session.delete(item)
                db.session.commit()

        return {'status':'deleated'}
