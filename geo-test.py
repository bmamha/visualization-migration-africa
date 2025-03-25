from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import pandas as pd

# Initialize Nominatim API
geolocator = Nominatim(user_agent="MyApp")


# To test geolocator is working
#
location = geolocator.geocode("Angola")

print("The latitude of the location is: ", location.latitude)
print("The longitude of the location is: ", location.longitude)


df = pd.read_csv("data/unhcr.csv")

country_list = list(set(df["Country"].values.tolist()))

geocode = RateLimiter(geolocator.geocode)

Geo_list = []

for country in country_list:
    location = geocode(country)
    Geo_list.append([country, location.latitude, location.longitude])

columns = ["country", "lat", "long"]

df_geo = pd.DataFrame(Geo_list, columns=columns)

df_geo.to_csv("data/Geolocation.csv")
