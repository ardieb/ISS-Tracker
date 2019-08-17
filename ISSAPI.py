import concurrent.futures
import asyncio
import requests
import os
import pandas as pd
from datetime import datetime


def noblock(f):
  async def wrapper(*args, **kwargs):
    with concurrent.futures.ThreadPoolExecutor(max_workers = 20) as executor:
      loop = asyncio.get_event_loop()
      response = await loop.run_in_executor(executor, lambda: f(*args, **kwargs))
    return response
  return wrapper


class ISS:

  def __init__(self):
    if os.path.isfile('ISS.csv'):
      df = pd.read_csv('ISS.csv', sep = ',')
    else:
      df = pd.DataFrame(
        columns = [
          'timestamp',
          'date',
          'longitude',
          'latitude',
          'altitude',
          'velocity',
          'visibility',
          'units'
          ])
    self._data = df

  def where(self):
    response = requests.get('https://api.wheretheiss.at/v1/satellites/25544')
    response.raise_for_status()
    js = response.json()

    lon, lat, alt, vel = js['longitude'], js['latitude'], js['altitude'], js['velocity']
    ts, vis, units = js['timestamp'], js['visibility'], js['units']

    row = {
      'timestamp': ts,
      'date': datetime.utcfromtimestamp(ts),
      'longitude': lon,
      'latitude': lat,
      'altitude': alt,
      'velocity': vel,
      'visibility': vis,
      'units': units,
      }

    self._data = self._data.append(row, ignore_index = True)

    return row

  def cache(self):
    self._data.to_csv('ISS.csv', sep = ',')

  @property
  def df(self):
    return self._data





