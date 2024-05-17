"""
Here the region-specific inflation adjusted discount rate will be computed

Based on the location, data from the World Databank gets used in the file 
"""
import pandas as pd
# Import the World Bank data access module to input real-time data
import wbgapi as wb 
# Import the python API for converting country names into Alpha-3 ISO-codes
import pycountry_convert
# Import APIs that are needed to determine the country from location
import certifi
import ssl
import geopy.geocoders
from geopy.geocoders import Nominatim

# Verify the SSL-certificate in order to be able to access the Nominatim geolocator
ctx = ssl.create_default_context(cafile=certifi.where())
geopy.geocoders.options.default_ssl_context = ctx

class Inflation():
    
    def locationToName(latitude, longitude, language = 'en'):
        """
        Gets the name of the country from the latitude and longitude information

        Args: 
            latitude: latitude of the position in the world 
            longitude: longitude of the position in the world

        Returns:
            country: name the country where the location is
        """
        # Initialize a geocoder (Nominatim in our case)
        app = Nominatim(user_agent="LCOE_model")
        coordinates = f"{latitude}, {longitude}"
        # Based on the input of latitude and longitude get the address and from it the country
        location = app.reverse(coordinates, language='en')
        address = location.raw['address']
        country = address.get('country', '')
        # Return the location's country name
        return(country)        
    
    def countryToISO3(country):
        """
        Gets the ISO-2 name of the country from the countries name

        Args:
            country: name of the country

        Returns:
            ISO: Alpha-3 code of the country
        """
        # Use the pycountry python package to get the ISO 
        ISO = pycountry_convert.country_name_to_country_alpha3(country, cn_name_format="")
        # Return ISO 
        return(ISO)

    def getInflation(ISO):
        """
        Returns the current inflation rate of the wanted country (Imported from the World Bank database)

        Args:
            ISO: Alpha-3 code of the country

        Returns:
            Inflation: inflation rate in the country 
        """
        # Import inflation database for the wanted country in the last 20 years 
        InflationPanda = wb.data.DataFrame(['FP.CPI.TOTL.ZG'], ISO, time=range(2003, 2024), skipBlanks=True, columns='series')
        # Take the average
        sum = InflationPanda.sum().iloc[0]
        Inflation = sum / 20
        # Return the 20-year averaged inflation rate for wanted country
        return(Inflation)
        
class discountRate():
 
    def InfAdjRate(ISO):
        """
        Returns the inflation-adjusted discount rate for the wanted location

        Args:
            ISO: Alpha-3 code of the country

        Returns: 
            InfAdjRate: inflation adjusted discount rate
        """
        # The corporate tax rate for the country gets inputed into a dataset
        corporateRate = pd.read_csv(r"C:\Users\maxik\Desktop\ETH\Bachelorarbeit\Code\LCOE_model\databases\corporate.csv")
        corporateRate[corporateRate["ISO3"] == ISO]
        corporateRate = corporateRate.iloc[0]["Corporate Tax Rate"]
        # The world bank does not offer a EU dataset, thus a constant is being used here (so far)
        if(ISO == 'AUT'or'BEL'or'HRV'or'CYP'or'DEU'or'EST'or'FIN'or'FRA'or'GRC'or'IRL'or'ITA'or'LVA'or'LTU'or'LUX'or'XOM'or'NLD'or'PRT'or'SVK'or'SVN'or'ESP'):
            # (CHANGE TO THE CURRENT INTEREST RATE OF THE ECB)
            interestRate = 4.5
        else:
            # Get the interest rate in wanted country
            interestRatePanda = wb.data.get(['FR.INR.RINR'], ISO, mrv=1)
            interestRate = interestRatePanda.get('value')
        # Using the proposed equation from Aldersey-Williams and Rubert, 2019 we get the inflation adjusted discount rate
        infAdjRate = (((1 + interestRate/100)*(1 + Inflation.getInflation(ISO)/100))-1)*(1 - corporateRate/100)
        # Return the inflation adjusted discount rate
        return(infAdjRate)

