# MAD_2_Project
 Modern Application Development Project 2 ( Ticket Booking APP) 


pip install bcrypt


## run the app:
cd '/mnt/c/Users/Sharonno/Desktop/MAD-2 project/MAD_2_Project'; python3 main.py

## run celery:
celery -A main.celery worker -l info

## run redis:
redis-server