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
current_lat_long_tuple = None

# variables to set in update
current_place = ""
current_lat = -1
current_long = -1
current_match_count = 0
multiple_match_details = ""
current_has_error = 0
current_error_text = ""

# database connection variables
db_host = ""
db_port = ""
db_username = ""
db_password = ""
db_database = ""

# connect to database.
my_db = MySQLdb.connect( host = db_host, port = db_port, user = db_username, passwd = db_password, db = db_database )

# create cursors
my_cursor = my_db.cursor( MySQLdb.cursors.DictCursor )
my_update_cursor = my_db.cursor( MySQLdb.cursors.DictCursor )

# select 5 rows in the table.
#my_cursor.execute( "SELECT * FROM outdoor_cafes LIMIT 5" )
#my_cursor.execute( "SELECT * FROM outdoor_cafes WHERE id = 4" )
my_cursor.execute( "SELECT * FROM outdoor_cafes" )

# get number of rows
row_count = int( my_cursor.rowcount )

# get google geocoding object.
# based on this commit: https://github.com/jbouvier/geopy/commit/c2f2e9137eef0c0eafdab39071ba1e7d70e38a8ei
my_client_id = ""
my_secret_key = ""
google_geo = geopy.geocoders.GoogleV3( client_id = my_client_id, secret_key = my_secret_key )

# loop, geocoding each.
for i in range( row_count ):

    # get next row, address
    current_row = my_cursor.fetchone()
    current_id = current_row[ "id" ]
    current_address = current_row[ "location" ]
    
    # transformations:
    # LA SALLE ==> LASALLE
    #if "LA SALLE" in current_address:
    
        # replace LA SALLE with LASALLE
        #current_address = current_address.replace( "LA SALLE", "LASALLE" )
        
    #-- END check for LA SALLE --# 
    
    # Special character between IRVING and PARK
    #try:
    
        # convert to unicode
        #current_address = current_address.decode()
        
        # convert to ASCII
        #current_address.encode( 'ascii', 'strict' )
        
    #except:
    
        # bad characters - not fighting it.  Convert to spaces.
        #current_address = current_address.encode( 'ascii', errors = 'replace' )
        #current_address = current_address.replace( '?', ' ' )

    #-- END check for illegal characters --#
        
    current_place = ""
    current_lat = ""
    current_long = ""
    current_match_count = 0
    multiple_match_details = ""
    current_has_error = 0
    current_error_text = ""
    
    print( "Location: " + current_address )

    # geocode, output the result.
    try:
    
        geocode_result_list = list( google_geo.geocode( current_address, exactly_one = False ) )
        
        #for current_place, ( current_lat, current_long ) in geocode_result_list:
        for current_geocode in geocode_result_list:
            
            current_match_count += 1
            
            if ( current_match_count == 1 ):

                # use first match.
                current_place = current_geocode[ 0 ]
                current_lat_long_tuple = current_geocode[ 1 ]
                current_lat = str( current_lat_long_tuple[ 0 ] )
                current_long = str( current_lat_long_tuple[ 1 ] )
                
                print( "- id %i - %s: %s, %s" % ( current_id, current_place, current_lat, current_long ) )
                
            else:
            
                # for second and subsequent matches, append them to 
                multiple_match_details += "%s: %s, %s\n" % ( current_geocode[ 0 ], str( current_geocode[ 1 ][ 0 ] ), str( current_geocode[ 1 ][ 1 ] ) )
            
            #-- END check to see if multiple matches. --#
            
        #-- END loop over geocode results. --#
        
    except Exception as e:
    
        print( "- Exception thrown geocoding:" )
        exception_type, exception_value, exception_traceback = sys.exc_info()
        print( "    - args = " + str( e.args ) )
        print( "    - type = " + str( exception_type ) )
        print( "    - value = " + str( exception_value ) )
        print( "    - traceback = " + str( exception_traceback ) )
        
        # create and store error string, set 
        current_has_error = 1
        current_error_text = "Exception thrown geocoding:\n"
        current_error_text += "- args = " + str( e.args ) + "\n"
        current_error_text += "- type = " + str( exception_type ) + "\n"
        current_error_text += "- value = " + str( exception_value ) + "\n"
        current_error_text += "- traceback = " + str( exception_traceback ) + "\n"
        
    #-- END try/except around geocoding. --#
    
    # update row.
    update_sql = "UPDATE outdoor_cafes SET"
    update_sql += " geocode_address = '%s'" % ( current_place )
    update_sql += ", geocode_latitude = '%s'" % ( current_lat )
    update_sql += ", geocode_longitude = '%s'" % ( current_long )
    update_sql += ", geocode_match_count = %i" % ( current_match_count )
    update_sql += ", geocode_multiple_match_details = '%s'" % ( multiple_match_details )
    update_sql += ", geocode_has_error = %i" % ( current_has_error )
    update_sql += ", geocode_error_details = '%s'" % ( current_error_text.replace( "'", '"' ) )
    update_sql += " WHERE id = %i" % ( current_id )
    
    print( "==> " + update_sql )
    my_update_cursor.execute( update_sql )
    my_db.commit()
    
#-- END loop over records. --#

# close cursors
my_cursor.close()
my_update_cursor.close()
my_db.close()
