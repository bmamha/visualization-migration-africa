from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import pandas as pd

# Initialize Nominatim API
geolocator = Nominatim(user_agent="MyApp")

df = pd.read_csv("data/unhcr.csv")

country_list = list(set(df["Country of Origin"].values.tolist()))

geocode = RateLimiter(geolocator.geocode)

Geo_list = []

for country in country_list:
    try:
        location = geocode(country)
        Geo_list.append([country, location.latitude, location.longitude])
    except:
        print(f"location: {country} not supported")

columns = ["country", "latitude", "longitude"]

df_geo = pd.DataFrame(Geo_list, columns=columns)

df_geo.to_csv("origin.csv")
