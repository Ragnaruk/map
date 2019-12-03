"""
https://nbviewer.jupyter.org/github/python-visualization/folium/tree/master/examples/
"""
import folium
import pickle
import os.path
from folium.plugins import MarkerCluster
from geopy.geocoders import ArcGIS
from geopy.exc import GeocoderTimedOut


def get_locations():
    """
    Parse CSV file and get coordinates for all cities within.
    Locations are cached for future calls.
    """
    if os.path.isfile('locations.pickle'):
        with open('locations.pickle', 'rb') as file:
            locations = pickle.load(file)
    else:
        locations = {}

    with open('locations.csv', 'r') as file:
        cities = [x.split(';')[0:2] for x in file.read().split('\n')]

    geolocator = ArcGIS(scheme='http')

    added_cities = 0
    skipped_cities = 0
    unknown_cities = 0
    try:
        for city in cities:
            if city[1] not in locations.keys():
                try:
                    locations[city[1]] = geolocator.geocode(city[1], timeout=10).raw['location']
                except AttributeError:
                    print("Unknown city {0}".format(city[1]))
                    unknown_cities += 1
                    continue

                print("Added {0} city.".format(city[1]))
                added_cities += 1
            else:
                print("Skipped {0} city.".format(city[1]))
                skipped_cities += 1
    except GeocoderTimedOut:
        print("Geocoder timed out.")
    except KeyboardInterrupt:
        print("Keyboard interrupt.")
    except Exception:
        print("Unknown exception.")

    with open('locations.pickle', 'wb') as file:
        pickle.dump(locations, file)

    print("Added: {0} / Skipped: {1} / Unknown: {2} / Total: {3}".format(
        added_cities, skipped_cities, unknown_cities, added_cities + skipped_cities + unknown_cities
    ))

    return locations


def create_map():
    """
    Create an OSM-based map with location markers and save it to html file.
    """
    # https://deparkes.co.uk/2016/06/10/folium-map-tiles/
    m = folium.Map(
        location=[0, 0],
        tiles='Cartodb Positron',
        zoom_start=1
    )

    marker_cluster = MarkerCluster(
        name='CAT Locations',
        overlay=True,
        control=False,
        icon_create_function=None
    )

    locations = get_locations()
    for k in locations.keys():
        location = locations[k]['y'], locations[k]['x']
        marker = folium.Marker(location=location)
        popup = '{0}'.format(k)

        folium.Popup(popup).add_to(marker)
        marker_cluster.add_child(marker)

    marker_cluster.add_to(m)
    folium.LayerControl().add_to(m)

    m.save('map.html')


if __name__ == '__main__':
    create_map()
