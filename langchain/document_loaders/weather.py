"""Simple reader that reads weather data from OpenWeatherMap API"""
from typing import List, Iterator

from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader
from datetime import datetime

class WeatherDataLoader(BaseLoader):
    """Weather Reader.
    Reads the forecast & current weather of any location using OpenWeatherMap's free API.
    Check 'https://openweathermap.org/appid' \
    on how to generate a free OpenWeatherMap API, It's free.

    Args:
        token (str): bearer_token that you get from OWM API.
    """

    def __init__(
        self,
        token: str,
    ) -> None:
        """Initialize with parameters."""
        super().__init__()
        self.token = token

    def lazy_load(
        self,
        places: List[str], 
    ) -> Iterator[Document]:
        """A lazy loader for document content."""

        try:
            import pyowm
        except:
            raise ValueError('install pyowm using `pip install pyowm`')

        owm = pyowm.OWM(api_key=self.token)
        mgr = owm.weather_manager()
        reg = owm.city_id_registry()

        results: List[Document] = []

        for place in places:
            info_dict = {}
            list_of_locations = reg.locations_for(city_name=place)

            try:
                city = list_of_locations[0]
            except:
                raise ValueError(f"The given location - {place}, "
                                 "cannot be found on OpenWeatherMap's city registry. "
                                 "Check the spelling and try again")
            lat = city.lat
            lon = city.lon

            metadata = {'queried_at':datetime.now()}
            res = mgr.one_call(lat=lat,lon=lon)

            info_dict['location'] = place
            info_dict['latitude'] = lat
            info_dict['longitude'] = lon
            info_dict['timezone'] = res.timezone
            info_dict['current weather'] = res.current.to_dict()
            if res.forecast_daily:
                info_dict['daily forecast'] = [i.to_dict() for i in res.forecast_daily]
            if res.forecast_hourly:
                info_dict['hourly forecast'] = [i.to_dict() for i in res.forecast_hourly]
            if res.forecast_minutely:
                info_dict['minutely forecast'] = [i.to_dict() for i in res.forecast_minutely]
            if res.national_weather_alerts:
                info_dict['national weather alerts'] = [i.to_dict() for i in res.national_weather_alerts]
            
            yield Document(page_content=str(info_dict),metadata=metadata)        

    def load(
        self, 
        places: List[str], 
    ) -> List[Document]:

        """Load weather data for the given locations. 
        OWM's One Call API provides the following weather data for any geographical coordinate:
        - Current weather
        - Hourly forecast for 48 hours
        - Daily forecast for 7 days
        Args:
            places (List[str]) - places you want the weather data for.
        """
        return list(self.lazy_load(places=places))