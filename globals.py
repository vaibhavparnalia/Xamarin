#globals.py
import datetime

currentYear = int(datetime.datetime.now().strftime("%Y"))
nowShowingURL = "http://www.imdb.com/showtimes/location"
moviePageURL = "http://www.imdb.com/title/"
fullcreditsExtn = "/fullcredits/"

#Saves time
parseBreaker_uncreditedCast = "Rest of cast listed alphabetically"
parseBreaker_birthDate = "Contact Info:"
