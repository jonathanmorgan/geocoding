'''
Copyright 2013 Jonathan Morgan

This file is part of http://github.com/jonathanmorgan/geocoding.

geocoding is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Foobar is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with http://github.com/jonathanmorgan/geocoding.  If not, see
<http://www.gnu.org/licenses/>.
'''

# imports
import geopy
import MySQLdb
import sys

# declare variables
my_db = None
my_cursor = None
row_count = -1
google_geo = None
current_row = None
current_address = ""
geocode_result_list = None
current_geocode = None
current_place = ""
current_lat_long_tuple = None
current_lat = -1
current_long = -1

# connect to database.
db_host = ""
db_port = ""
db_username = ""
db_password = ""
db_database = ""

# connect to database.
my_db = MySQLdb.connect( host = db_host, port = db_port, user = db_username, passwd = db_password, db = db_database )

# create cursor
my_cursor = my_db.cursor( MySQLdb.cursors.DictCursor )

# select 5 rows in the table.
my_cursor.execute( "SELECT * FROM outdoor_cafes LIMIT 5" )

# get number of rows
row_count = int( my_cursor.rowcount )

# get google geocoding object.
geocoder = geopy.geocoders.GeocoderDotUS()

# loop, geocoding each.
for i in range( row_count ):

    # get next row, address
    current_row = my_cursor.fetchone()
    current_address = current_row[ "location" ]
    
    print( "Location: " + current_address )

    # geocode, output the result.
    try:
    
        #geocode_result_list = list( geocoder.geocode( current_address, exactly_one = False ) )
        
        #for current_place, ( current_lat, current_long ) in geocode_result_list:
        #for current_geocode in geocode_result_list:
            
        current_geocode = geocoder.geocode( current_address, exactly_one = False )
    
        current_place = current_geocode[ 0 ]
        current_lat_long_tuple = current_geocode[ 1 ]
        current_lat = current_lat_long_tuple[ 0 ]
        current_long = current_lat_long_tuple[ 1 ]
        
        print( "- %s: %f, %f" % ( current_place, current_lat, current_long ) )
            
        #-- END loop over geocode results. --#
        
    except Exception as e:
    
        print( "- Exception thrown geocoding:" )
        exception_type, exception_value, exception_traceback = sys.exc_info()
        print( "    - args = " + str( e.args ) )
        print( "    - type = " + str( exception_type ) )
        print( "    - value = " + str( exception_value ) )
        print( "    - traceback = " + str( exception_traceback ) )
        
    #-- END try/except around geocoding. --#
    
#-- END loop over records. --#

# close cursors
my_cursor.close()
my_db.close()
