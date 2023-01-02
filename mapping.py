import os
import requests

from dotenv import load_dotenv
load_dotenv()

API_KEY = os.environ.get("MAPQUEST_API_KEY")

def get_map_url(address, city, state):
    """Get MapQuest URL for a static map for this location."""

    base = f"https://www.mapquestapi.com/staticmap/v5/map?key={API_KEY}"
    where = f"{address},{city},{state}"
    return f"{base}&center={where}&size=@2x&zoom=15&locations={where}"


def save_map(id, address, city, state):
    """Get static map and save in static/maps directory of this app."""

    # read from request
    resp = requests.get(get_map_url(address, city, state))
    # path to directory
    path = os.path.abspath(os.path.dirname(__file__))

    # write contents of file to path
    with open(f"{path}/static/maps/{id}.jpg", 'wb') as wf: # opens in write mode.
        wf.write(resp.content)