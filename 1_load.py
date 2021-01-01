#importing libraries and ignoring ssl errors.
from urllib.request import urlopen
from pathlib import Path
import json
import ssl
import time
import sys
import sqlite3
import xml.etree.ElementTree as ET

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

#Setting up data folder, and file paths
try:
    root_dir = Path(__file__).parent
    data_folder = root_dir / 'data'
    db_file = data_folder / 'db_landings.sqlite'
    js_local = data_folder / 'source_data/gh4g-9sfh.json'
    xml_local = data_folder / 'source_data/gh4g-9sfh.xml'
except:
    print('Error setting up file paths, check README.txt for setup guide.')
    quit()

#Creating tables if they dont exist
conn = sqlite3.connect(db_file)
cur = conn.cursor()

cur.executescript('''
CREATE TABLE IF NOT EXISTS Fall (
    id          INTEGER NOT NULL PRIMARY KEY UNIQUE,
    fall        TEXT UNIQUE
);
CREATE TABLE IF NOT EXISTS Class (
    id         INTEGER NOT NULL PRIMARY KEY UNIQUE,
    class       TEXT UNIQUE
);
CREATE TABLE IF NOT EXISTS Geolocation (
    id          INTEGER NOT NULL PRIMARY KEY UNIQUE,
    latitude    FLOAT,
    longitude   FLOAT,
    UNIQUE      (latitude, longitude)
);
CREATE TABLE IF NOT EXISTS Meteorite (
    fall_id     INTEGER,
    class_id    INTEGER,
    geo_id      INTEGER,
    id          INTEGER PRIMARY KEY UNIQUE,
    name        TEXT UNIQUE,
    mass        FLOAT,
    year        INTEGER CHECK(LENGTH(year) <= 4)
)
''')

#Defining functions for later use:
def load_data(url, context):
    data_type = None
    data = None
    if url.endswith('.json'):
        data_type = 'json'
    if url.endswith('.xml'):
        data_type = 'xml'

    try:
        print('Retreiving')
        data = uh = urlopen(url, context = ctx)
        data = uh.read().decode()
        print('Retreived', len(data), 'characters')
    except: data = None

    return(data_type, data)

def ass_vals(item, data_type):
    error = False
    v_dict = dict()
    if data_type == 'xml':
        try:
            v_dict.update(id = item.find('id').text)
            v_dict.update(name = item.find('name').text)
            v_dict.update(mass = item.find('mass').text)
            v_dict.update(recclass = item.find('recclass').text)
            v_dict.update(lat = item.find('geolocation').get('latitude'))
            v_dict.update(long = item.find('geolocation').get('longitude'))
            v_dict.update(year = item.find('year').text.split('-')[0])
            v_dict.update(fall = item.find('fall').text)
        except: error = True

    if data_type == 'json':
        try:
            v_dict.update(id = item['id'])
            v_dict.update(name = item['name'])
            v_dict.update(mass = item['mass'])
            v_dict.update(recclass = item['recclass'])
            v_dict.update(lat = item['geolocation']['latitude'])
            v_dict.update(long = item['geolocation']['longitude'])
            v_dict.update(year = item['year'].split('-')[0])
            v_dict.update(fall = item['fall'])
        except: error = True

    if (error is False and (float(v_dict.get('lat')), float(v_dict.get('long')))
    != (0, 0) and float(v_dict.get('mass')) != 0):
        return(v_dict.get('id'), v_dict.get('name'), v_dict.get('mass'),
            v_dict.get('recclass'), v_dict.get('lat'), v_dict.get('long'),
            v_dict.get('year'), v_dict.get('fall'))
    else: return(None)


def sql_inject(id, name, mass, recclass, lat, long, year, fall, iter, c_inter):
    cur.execute('INSERT OR IGNORE INTO Fall (fall) VALUES (?)', (fall, ))
    cur.execute('SELECT id FROM Fall WHERE fall = ?', (fall, ))
    fall_id = cur.fetchone()[0]

    cur.execute('INSERT OR IGNORE INTO Class (class) VALUES (?)', (recclass, ))
    cur.execute('SELECT id FROM Class WHERE class = ?', (recclass, ))
    class_id = cur.fetchone()[0]

    cur.execute('''
        INSERT OR IGNORE INTO Geolocation (latitude, longitude)
        VALUES (?, ?)''', (lat, long))
    cur.execute('''
        SELECT id FROM Geolocation WHERE (latitude, longitude) = (?, ?)''',
        (lat, long))
    geo_id = cur.fetchone()[0]

    cur.execute('''
        INSERT OR IGNORE INTO Meteorite (fall_id, class_id, geo_id, id, name,
            mass, year)
        VALUES (?, ?, ?, ?, ?, ?, ?)''', (fall_id, class_id, geo_id, id, name,
            mass, year))

#Silly animation to indicate th program is actually writing to the database
#and only commiting changes in a certain interval defined by "c_inter".
    if iter % int(c_inter) == 0:
        conn.commit()
        if (iter / c_inter) % 3 == 1:
            sys.stdout.write('   \b\b\b')
            sys.stdout.write('.')
            sys.stdout.flush()
        if (iter / c_inter) % 3 == 2:
            sys.stdout.write('.')
            sys.stdout.flush()
        if (iter / c_inter) % 3 == 0:
            sys.stdout.write('.')
            sys.stdout.flush()
            sys.stdout.write('\b\b\b')
        time.sleep(0.5)

##################=====NASA data on meteorite landings=====####################
#            https://data.nasa.gov/api/views/gh4g-9sfh/rows.xml               #
#              https://data.nasa.gov/resource/gh4g-9sfh.json                  #
###############################################################################

#Count variable to keep track of new entries later
cur.execute('SELECT COUNT (*) FROM Meteorite')
count_old = cur.fetchone()[0]

#Letting user input data source or choose local data file, opening and loading
#raw string data into variable 'data' and data type into variable 'data_type'
while True:
    url = input('Enter data source or press "Enter" for local file\nSource: ')
    if len(url) < 1:
        inp = input('Enter "sample" for shortened data set (~1000 entries)\n'+
            'or "full" for complete data set (~46000 entries)\n'+
            'If you want to exit, enter "end" or press the Enter key\n'+
            'Sample/Full: ')
        if len(inp) < 1 or inp == 'end': quit()
        if inp != 'sample' and inp != 'full':
            print('Invalid input. Try again\n')
            continue
        if inp == 'sample':
            try:
                data = open(js_local, encoding = 'utf8').read()
                data_type = 'json'
                break
            except:
                print('File not found. Try'+
                    '"https://data.nasa.gov/resource/gh4g-9sfh.json"'+
                    'as data source.\n')
                continue

        if inp == 'full':
            try:
                data = open(xml_local, encoding = 'utf8').read()
                data_type = 'xml'
                break
            except:
                print('File not found. Try'+
                    '"https://data.nasa.gov/resource/gh4g-9sfh.xml"'+
                    'as data source.\n')
                continue
    else:
        if url == 'end': quit()
        raw_data = load_data(url, ctx)
        data_type = raw_data[0]
        data = raw_data[1]

    if data_type is None or data is None:
        print('Failiure to retreive data')
        continue
    else: break

#Checking type of data and storing formatted string data in variable "data_str"
#based on data type
if data_type == 'xml':
    try:
        tree = ET.fromstring(data)
        data_str = tree.findall('row/row')
        print('Loading', len(data_str), 'entries to db_landings.sqlite\n'+
            'Working', end ='')
    except:
        print('Error loading .xml data! Check README.txt for setup guide')
        quit()

if data_type == 'json':
    try:
        data_str = json.loads(data)
        print('Loading', len(data_str), 'entries to db_landings.sqlite\n'+
            'Working...', end = '')
    except:
        print('Error loading .json data! Check README.txt for setup guide')
        quit()

#creating iteration variable "i" to 0 and commit interval "c_inter" to a
#reasonable value
i = 0
c_inter = 500
#Assigning values from dataset into "vals", then passing data into
#sql_inject function, for each item in string data.
for item in data_str:
    vals = ass_vals(item, data_type)
    if vals is not None:
        i = i + 1
        sql_inject(*(vals + (i,) + (c_inter,)))
    else: continue
conn.commit()

#Checking amount of new entriees in Meteorite table, comparing old count to new
cur.execute('SELECT COUNT (*) FROM Meteorite')
count_new = cur.fetchone()[0]
print('\nFinished.', count_new - count_old, 'new entries in Meteorite table.\n'+
    'Ignored', len(data_str) - count_new, 'entries due to incomplete data')

conn.close()

print('Run "dump.py" to compile javascript file containing data from database.')
##########===SQL command to view combined data in SQlite browser:===###########
#SELECT Meteorite.id, Meteorite.name, Meteorite.mass, Class.class, Fall.fall,
#Geolocation.latitude, Geolocation.longitude, Meteorite.year FROM Meteorite
#JOIN Class JOIN Geolocation JOIN Fall ON Meteorite.geo_id = Geolocation.id AND
#Meteorite.class_id = Class.id AND Meteorite.fall_id = Fall.id
#ORDER BY Meteorite.year
