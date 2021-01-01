import sqlite3
import json
import codecs
import os
from pathlib import Path

#Deleting landings.js if already exists
if os.path.exists('landings.js'):
  os.remove('landings.js')

#Setting up file paths
try:
    root_dir = Path(__file__).parent
    data_folder = root_dir / 'data'
    db_file = data_folder / 'db_landings.sqlite'
    js_file = data_folder / 'landings.js'
except:
    print("Error setting up file paths, check README.txt for instructions")
    quit()

#Function to check if range inputs are valid depending on the category chosen
def check_range(f_cat, rangemin, rangemax):
    if f_cat == 'year':
        try:
            rangemin = int(rangemin)
            rangemax = int(rangemax)
        except:
            return False

        if rangemin <= rangemax and rangemin >= 0 and rangemax < 2030:
            return True
        else:
            return False
    if f_cat == 'mass':
        try:
            rangemin = float(rangemin)
            rangemax = float(rangemax)
        except:
            return False

        if rangemin <= rangemax and rangemin > 0:
            return True
        else:
            return False
    else:
        return False

#Opening files, joining data from database tables and sorting by year.
conn = sqlite3.connect(db_file)
cur = conn.cursor()
cur.execute('''SELECT Meteorite.id, Meteorite.name, Meteorite.mass,
    Class.class, Fall.fall, Geolocation.latitude, Geolocation.longitude,
    Meteorite.year FROM Meteorite JOIN Class JOIN Geolocation JOIN Fall ON
    Meteorite.geo_id = Geolocation.id AND Meteorite.class_id = Class.id AND
    Meteorite.fall_id = Fall.id ORDER BY Meteorite.year''')
fhand = codecs.open(js_file, 'w', 'utf-8')

#Letting user chose category to filter by and define ranges for said catgory
while True:
    f_cat = input('Select category to filter by'+
                '\n(mass, year, fall, all)'+
                '\nFilter by: ')
    if f_cat == 'all':
        break
    elif f_cat == 'fall':
        f_range = input('Fell / Found: ')
        if f_range != 'Fell' and f_range != 'Found':
            print('Invalid range, check README.txt')
            continue
        else:
            break
    elif f_cat != 'mass' and f_cat != 'year':
        print('Invalid category')
        continue
    else:
        rangemin = input('Select range min: ')
        rangemax = input('Select range max: ')
        check = check_range(f_cat, rangemin, rangemax)
        if check == True:
            f_range = (rangemin, rangemax)
            break
        else:
            print('Invalid range, check README.txt')
            continue

#Writing data from database to .js file formatted as an object containing many
#objects, only writing the entry if chosen catgory is within chosen range.

#Writing header to file and creating count variable to keep track of number
#of entries
fhand.write('mData = {\n')
count = 0

for row in cur:
    id = str(row[0])
    name = str(row[1])
    mass = str(row[2])
    m_class = str(row[3])
    fall = str(row[4])
    lat = str(row[5])
    long = str(row[6])
    year = str(row[7])

#Creating in_range variable and setting to False, so the entry will not be
#written unless chosen value is in range.
    in_range = False

    if f_cat == 'fall':
        if fall == f_range:
            in_range = True
        else:
            continue

    if f_cat == 'mass':
        if float(f_range[0]) <= float(mass) <= float(f_range[1]):
            in_range = True
        else:
            continue

    if f_cat == 'year':
        if int(f_range[0]) <= int(year) <= int(f_range[1]):
            in_range = True
        else:
            continue

    if f_cat == 'all':
        in_range = True

    if in_range == True:
        count = count + 1
        if count > 1: fhand.write(',\n')
#Formatting the output to be valid javascript
        output = ('    '+id+': {'+'\n        id: '+id+','+'\n        name: "'+
            name+'",'+'\n        geo: {lat: '+lat+', lng: '+long+'},'+
            '\n        '+'fall: "'+fall+'",\n        year: '+year+
            ',\n        m_class: "'+m_class+'",\n        mass_g: '+mass+
            '\n    }')
#Writing enties to file.
        for line in output:
            fhand.write(str(line))
    else:
        continue

fhand.write('\n};\n')

cur.close()
fhand.close()
print(count, 'records written to landings.js')
print('Open "map.html" in a browser to view visualized data')
