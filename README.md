# Meteorite Landings
This is a collection of programs to collect and visualize data on meteorite landings. To run them you need to have a version of Python 3 installed. To find the latest release of Python go to: https://www.python.org/downloads/

## NASA data on meteorite landings:
Full data set (~45 000 entries):  
https://data.nasa.gov/api/views/gh4g-9sfh/rows.xml

Sample data set (1 000 entries):  
https://data.nasa.gov/resource/gh4g-9sfh.json

## SQL command to view combined data in SQlite browser:
> SELECT Meteorite.id, Meteorite.name, Meteorite.mass, Class.class, Fall.fall, Geolocation.latitude, Geolocation.longitude, Meteorite.year FROM Meteorite JOIN Class JOIN Geolocation JOIN Fall ON Meteorite.geo_id = Geolocation.id AND Meteorite.class_id = Class.id AND Meteorite.fall_id = Fall.id ORDER BY Meteorite.year

# Guide
Once you have Python installed you need to make sure you have a folder named "data" in the main project folder, and another folder named "scource_data" in the "data" folder. Once you have those set up correctly run the programs in the following order:

1. 1_load.py - You will be prompted to use web data or local data.
      - For web data you can use one of the links at the top of this file. Note the .json link is only sample data, containing around 1000 entries. The .xml link contains a complete data set of around 45000.
      - For local files, just press enter when prompted and enter "sample" for sample data or "full" for complete data set. Note that you have to have the local files saved under "#PROJECT_FOLDER/data/scource_data". To download theese files, just right click the links under "NASA data on meteorite landings:" and "save link as...", then save them in the correct location. I've included the sample data in this repository, but if you want to use the complete data set as a local file, you have to download it manually.
      - If the sqlite database named "db_landings.sqlite" alrady exists, the program will just add the entries it can't find in the existing database. To start from scratch simply delete "db_landings.sqlite from the data folder.

2. 2_dump.py - You will be asked to filter results by category.
      - If you want to include all entries from DB, enter "all".
      - If you want to sort by mass, enter "mass", then enter the minimum and maximum mass to include in grams(!)
      - If you want to sort by year, enter "year", then enter the earliest and the latest year to include.
      - If you want to sort by Fell/Found, enter "fall", then enter whether you want to filter by "Fell" or "Found", "Fell" means the meteorite was detected at the time of impact, while Found means it was found and dated at a later time.

3. map_circles.html or map_markers.html
      - map_circles is a map with circular markers scaled after the recovered mass of the meteorite, be carful if opening this without filtering out any results from the database while using the complete data set, as this will run very poorly in your browser.
      - map_markers is a map with markers containing metadata about the meteorite, such as name, mass, class, Fell/Found, year and id from the original database this data is taken from.

## API Keys
Note that an API key is required to properly view the maps. You can get an API key at: https://developers.google.com/maps/documentation/javascript/get-api-key

If you already have an API key you need to change out the url at line 9 in map_markers.html and map_circles.html and instead use:

> https://maps.googleapis.com/maps/api/js?callback=initMap&key=#YOUR_API_KEY

Remember to change "#YOUR_API_KEY" to your actual key.
