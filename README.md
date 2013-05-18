# geocoding django app

## Installation

### django

- Make sure you have python installed.  Also, install setuptools (easy\_install) and then install pip.
- Install django:

        sudo pip install django

- In whatever directory you want to work in, create a django site:

        django-admin.py startproject <site_name>
    
- This will create a __site folder__ named "site\_name".  Inside it, there will be a file named "manage.py" and another folder named "site\_name".  Inside this __configuration folder__ will be settings.py, urls.py, and wsgi.py, the configuraiton files for your django database connection and site.

- Use git to pull this application into your django __site folder__:

        git clone ...

### Google docs interface

Now, we install the google data interface into our django site, so it is accessible by the geocoding application, following instructions here: [https://developers.google.com/gdata/articles/python\_client\_lib](https://developers.google.com/gdata/articles/python_client_lib)

- Install ElementTree python module.

        (sudo) pip install ElementTree
    
- Download and install the google data library.

    - From pip (try this first):

            (sudo) pip install gdata

    - From source (if you have problems and want to be able to run the test scripts):

        - First, go to the Google Code page for the gdata library: [https://code.google.com/p/gdata-python-client/](https://code.google.com/p/gdata-python-client/)
        - Then, download the latest (2.0.17 at the time of writing).  Download page: [https://code.google.com/p/gdata-python-client/downloads/list](https://code.google.com/p/gdata-python-client/downloads/list)
        - uncompress and unpack the tar.gz file that you downloaded.

                tar -xvzf gdata-2.0.17.tar.gz

        - Now, you need to compile and install it.  Go into the gdata directory the uncompress created.
        
            - To install system-wide:

                    sudo python setup.py install
                
            - To just install inside your home directory, for use by your user:
        
                    python setup.py install --home=<path_to_home_directory>

        - to test, from the source folder that you unpacked, run:
    
                ./tests/run_data_tests.py

### geopy

Install geopy using pip:

    sudo pip install geopy
    
## Usage

Right now, there are two scripts you can look at to see how to geocode with geopy:

- google\_geocode\_test.py - to actually run this, you'll need to make a copy of the file, then edit the following:
    - database information in the "db\_" variables (db\_host, db\_port, db\_username, db\_password, db\_database).
    - Update the queries so they reference the appropriate tables and columns for your database.
    - If you have a google maps for business account, set my\_client\_id and my\_secret\_key to the values google sent you when you signed up.
    
- geocoder.us\_geocode\_test.py - this one reads from database, doesn't write to it.  In it, you'll have to make a copy of the file, then:
    - database information in the "db\_" variables (db\_host, db\_port, db\_username, db\_password, db\_database).
    - Update the queries so they reference the appropriate tables and columns for your database.
    
Very soon, there will be a django application that you can use to make batch geocoding requests from multiple sources like google docs or a database table, then have them run in the background, notifying you of problems or completion via email.  Not just yet, however.

## License

Copyright 2013 Jonathan Morgan

This file is part of [http://github.com/jonathanmorgan/geocoding](http://github.com/jonathanmorgan/geocoding).

geocoding is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Foobar is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with [http://github.com/jonathanmorgan/geocoding](http://github.com/jonathanmorgan/geocoding).  If not, see
[http://www.gnu.org/licenses/](http://www.gnu.org/licenses/).
