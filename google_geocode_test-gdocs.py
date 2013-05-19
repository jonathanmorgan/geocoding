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

# !TODO - see if we can get count of rows, pull in sets of rows, so we don't have the entire spreadsheet in memory at once.

# imports
import geopy
import MySQLdb
import sys
import xml.dom.minidom

# gdata
import gdata.docs.service
import gdata.spreadsheet.service
import gdata.spreadsheet.text_db

# functions
def _PrintFeed( feed ):
    for i, entry in enumerate(feed.entry):
        if isinstance(feed, gdata.spreadsheet.SpreadsheetsCellsFeed):
            print '%s %s\n' % (entry.title.text, entry.content.text)
        elif isinstance(feed, gdata.spreadsheet.SpreadsheetsListFeed):
            print '%s %s %s' % (i, entry.title.text, entry.content.text)
        
            # Print this row's value for each column (the custom dictionary is
            # built using the gsx: elements in the entry.)
            print 'Contents:'
            for key in entry.custom:  
                print '  %s: %s' % (key, entry.custom[key].text) 
            print '\n',
        else:
            print '%s %s\n' % (i, entry.title.text)

#-- END method _PrintFeed() --#


# declare variables

# connecting to google docs.
my_gdocs_client = None
username = ""
password = ""
document_id = ""
documents_feed = None

# geocoding.
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

# connect to google docs
username = ""
password = ""

# get spreadsheet client
my_gdocs_client = gdata.spreadsheet.service.SpreadsheetsService()
my_gdocs_client.email = username
my_gdocs_client.password = password
my_gdocs_client.source = 'Spreadsheets Geocoder'
my_gdocs_client.ProgrammaticLogin()

# get spreadsheet worksheets
curr_key = ""
curr_wksht_id = ""

worksheet_feed = my_gdocs_client.GetWorksheetsFeed( curr_key )

# print?
_PrintFeed( worksheet_feed )

# worksheet ID parts (is a URL, worksheet is last thing in URL path list - so,
#    split on "/", then take last thing as worksheet ID).
id_parts = worksheet_feed.entry[ 0 ].id.text.split( '/' )
curr_wksht_id = id_parts[ len( id_parts ) - 1 ]

# also, there is a title element, could ask for title, match that to get ID.
# OR, you could ask for worksheet number, then subtract one, get ID for that
#    entry index.

# pretty-print XML
xml = xml.dom.minidom.parseString( str( worksheet_feed ) )
pretty_xml_as_string = xml.toprettyxml()

# get list of rows...?
row_feed = my_gdocs_client.GetListFeed( curr_key, curr_wksht_id )

# get entry list
row_entry_list = row_feed.entry

# get a row.
test_row = row_entry_list[ 0 ]

# contents of row, as a string:
print( "Row contents: " + test_row.contents.text )

# API doc: https://developers.google.com/google-apps/spreadsheets/
# based in part on code in: http://mrwoof.tumblr.com/post/1004514567/using-google-python-api-to-get-rows-from-a-google

# to get the column data out, you use the text_db.Record class, then use the dict record.content
row_record = gdata.spreadsheet.text_db.Record( row_entry = test_row )

# get the "content" dict that is nested in row_record
row_content = row_record.content

# in dict, columns are named same as column name in first row, but all lower
#    case, and all spaces and underscores removed.

# update a value
row_content[ 'geocodeerrordetails' ] = "Hello!"

# update the row with a dictionary...
update_result = my_gdocs_client.UpdateRow( test_row, row_content )

# success?
if isinstance( update_result, gdata.spreadsheet.SpreadsheetsList ):

    print( 'Updated!' )

#-- END check to see if update succeeded. --#

# Need to work on pulling in only 100 rows at a time, or something, so you don't
#    end up with entire spreadsheet in memory.

# OR, could use this library: https://github.com/burnash/gspread
# available from pypi: pip install gspread
# doc: http://burnash.github.io/gspread/index.html
# EXCEPT it is slow.  Really slow.

import gspread

# Login with your Google account
gc = gspread.login( username, password )

# get spreadsheet:
gspread_spreadsheet = gc.open_by_key( curr_key )

# get worksheet
gspread_worksheet = gspread_spreadsheet.get_worksheet(0)

# get first row's values (headers)
row_1_values = gspread_worksheet.row_values( 1 )

# 2nd row
row_2_values = gspread_worksheet.row_values( 2 )

# update cell by cell (updates in real-time)
#wks.update_acell('B2', "it's down there somewhere, let me take another look.")

# also a batch update.

# get number of rows
row_count = len( row_entry_list )

# get google geocoding object.
# based on this commit: https://github.com/jbouvier/geopy/commit/c2f2e9137eef0c0eafdab39071ba1e7d70e38a8ei
my_client_id = ""
my_secret_key = ""
google_geo = geopy.geocoders.GoogleV3( client_id = my_client_id, secret_key = my_secret_key )

# loop, geocoding each.
for current_row_entry in row_entry_list:

    # to get the column data out, you use the text_db.Record class, then use the dict record.content
    row_record = gdata.spreadsheet.text_db.Record( row_entry = current_row_entry )

    # get the "content" dict that is nested in row_record
    row_content = row_record.content

    # get the address
    current_address = row_content[ "location" ]
    
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
    
    # update row values.
    row_content[ "geocodeaddress" ] = current_place
    row_content[ "geocodelatitude" ] = current_lat
    row_content[ "geocode_longitude" ] = current_long
    row_content[ "geocode_match_count" ] = current_match_count
    row_content[ "geocode_multiple_match_details" ] = multiple_match_details
    row_content[ "geocode_has_error" ] = current_has_error
    row_content[ "geocode_error_details" ] = current_error_text
    
    # update the row with a dictionary...
    update_result = my_gdocs_client.UpdateRow( current_row_entry, row_content )
    
    # success?
    if isinstance( update_result, gdata.spreadsheet.SpreadsheetsList ):
    
        print( 'Updated!' )
    
    #-- END check to see if update succeeded. --#
    
#-- END loop over records. --#