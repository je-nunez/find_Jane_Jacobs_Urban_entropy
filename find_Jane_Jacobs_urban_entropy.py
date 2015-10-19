#!/usr/bin/env python

"""
   Explore Jane Jacobs Urban entropy around a coordinate and add it into
   MongoDB for it to be queried later.
"""

# this is a first draft of the exploration of Jane Jacobs urban entropy
# pylint: disable-all

# PyMongo API is at the MongoDB website:
#
# http://api.mongodb.org/python/current/api/pymongo/collection.html
#

import datetime
import urllib2
import json
from pymongo import MongoClient


def add_entropy_to_mongodb(entropy_list):
    """Add entropy list into MongoDB."""

    # Open a connection to MongoDB

    client = MongoClient()

    # Open the db 'jane_jacobs_urban_entropy' in MongoDB

    db = client.jane_jacobs_urban_entropy

    # Add the entropy list into MongoDB

    db.google_entropy.insert_many(entropy_list)

    print "DEBUG: MongoDB collections: {0}".format(db.collection_names())

    for entropy_item in db.google_entropy.find({}):
        print entropy_item



# take latitude and longitude really by command-line arguments

latitude = 40.75773

longitude = -73.985708

Google_Geodecode_entropy_fmt = \
  "http://maps.googleapis.com/maps/api/geocode/json?language=en&latlng=%f%%2C%f&sensor=false"

# we are specially interested in the 'place_id' which gives the entropy around
# a coordinate

Google_Geodecode_entropy = Google_Geodecode_entropy_fmt % (latitude, longitude)

response = urllib2.urlopen(Google_Geodecode_entropy)

Google_entropy_json = response.read()

Google_entropy = json.loads(Google_entropy_json)

# print json.dumps(Google_entropy, indent=4, sort_keys=True)

if "status" in Google_entropy and Google_entropy["status"] == "OK" and \
   "results" in Google_entropy:
    add_entropy_to_mongodb(Google_entropy["results"])

