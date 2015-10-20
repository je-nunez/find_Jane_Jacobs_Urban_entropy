#!/usr/bin/env python

"""
   Explore Jane Jacobs Urban entropy around a coordinate and add it into
   MongoDB for it to be queried later.

   This program takes a coordinate as (latitude, longitude), not as
   (longitude, latitude).
"""

# The PyMongo API is at the MongoDB website:
#
# http://api.mongodb.org/python/current/api/pymongo/collection.html
#

import sys
import urllib2
import json
from pymongo import MongoClient


#
# class Location(object):
#

class Location(object):
    """A Location, ie., a coordinate."""

    # pylint: disable=too-few-public-methods

    def __init__(self, latitude, longitude):
        """Constructor."""
        # Private members and setters/getters, etc, will be added later.
        # This is a first version
        self.latitude = latitude
        self.longitude = longitude


def add_entropy_to_mongodb(entropy_list):
    """Add entropy list into MongoDB."""

    # Open a connection to MongoDB

    client = MongoClient()

    # Open the db 'jane_jacobs_urban_entropy' in MongoDB

    jane_jacobs_db = client.jane_jacobs_urban_entropy

    # Add the entropy list into MongoDB

    jane_jacobs_db.google_entropy.insert_many(entropy_list)

    print "DEBUG: MongoDB collections: {0}".\
        format(jane_jacobs_db.collection_names())

    for entropy_item in jane_jacobs_db.google_entropy.find({}):
        print "DEBUG: " + str(entropy_item)


def find_urban_entropy_gmaps(location):
    """
       Query Google Maps to find the places of interest around a coordinate.
    """

    gmaps_geodecode_url_fmt = (
        "http://maps.googleapis.com/maps/api"
        "/geocode/json?language=en&sensor=false"
        "&latlng=%f%%2C%f"
    )

    # we are specially interested in the 'place_id' returned by this geo-db,
    # which gives the entropy (places of interest) around a coordinate

    gmaps_entropy_url = gmaps_geodecode_url_fmt % (location.latitude,
                                                   location.longitude)

    response = urllib2.urlopen(gmaps_entropy_url)

    google_entropy_json = response.read()

    google_entropy = json.loads(google_entropy_json)

    # print json.dumps(google_entropy, indent=4, sort_keys=True)

    if "status" in google_entropy and google_entropy["status"] == "OK" and \
       "results" in google_entropy:
        add_entropy_to_mongodb(google_entropy["results"])


class Config(object):
    """
       Namespace to hold global config parameters affecting the logic of
       this program.
    """

    # pylint: disable=too-few-public-methods

    @classmethod
    def parse_config_and_cmd_line_args(cls):
        """
           Retrieve the coordinate passed as arguments in the command line.
           It can change global config parameters in this 'Config' namespace.

           Returns the location requested to find the entropy about.
        """

        import argparse
        from argparse import RawDescriptionHelpFormatter

        detailed_usage = get_this_script_docstring()
        summary_usage = 'Try to find Jane Jacobs Urban entropy at a ' \
                        'geographical location'

        # The ArgParser for the command-line: very simple for now

        parser = argparse.ArgumentParser(description=summary_usage,
                                         epilog=detailed_usage,
                                         formatter_class
                                         =RawDescriptionHelpFormatter
                                        )

        # We will use the Open Geospatial Consortium Well-Known Text (WKT) to
        # describe the argument in the command-line to get (or limit) the
        # Jane Jacobs urban entropy from.
        parser.add_argument('coord_components', metavar='COORDINATES',
                            nargs='+',
                            help="The coordinates of the location to find "
                                 "(estimate) the Jane Jacobs' Urban entropy.")

        args = parser.parse_args()

        coordinates = []

        if args.coord_components:
            if isinstance(args.coord_components, list):
                # this type check is necessary for some
                # argparse.ArgumentParser() installed in Mac OS/X
                coordinates = args.coord_components
            else:
                # normal case for argparse.ArgumentParser() in Linux
                coordinates = [args.coord_components]

        # Validate that there are two components in the coordinate passed as
        # arguments in the command line
        if len(coordinates) != 2:
            sys.stderr.write("Error: expected two components for coordinate\n")
            return None

        # Validate that the two components of the coordinate are
        # floating-points
        try:
            latitude = float(coordinates[0])
            longitude = float(coordinates[1])
        except ValueError:
            sys.stderr.write("Error: there is a component of the coordinate "
                             "which is not a floating-point")
            return None

        return Location(latitude, longitude)


def main():
    """Main function."""

    location = Config.parse_config_and_cmd_line_args()

    if location:
        find_urban_entropy_gmaps(location)


def get_this_script_docstring():
    """Utility function to get the Python docstring of this script"""
    import os
    import inspect

    current_python_script_pathname = inspect.getfile(inspect.currentframe())
    dummy_pyscript_dirname, pyscript_filename = \
                os.path.split(os.path.abspath(current_python_script_pathname))
    pyscript_filename = os.path.splitext(pyscript_filename)[0]  # no extension
    pyscript_metadata = __import__(pyscript_filename)
    pyscript_docstring = pyscript_metadata.__doc__
    return pyscript_docstring


if __name__ == '__main__':
    main()
