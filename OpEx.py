""" 
Calculate the Operational Expenditures 

The class OPEX() includes functions that compute the annual
costs for different components of the total cost
"""
# First we import all the used python packages
import pandas as pd
import pycountry_convert
import wbgapi as wb


class OPEX():

    def __init__(self, D_rotor_array, Power_rated_array, hub_height_array, d, AEP, ISO):
        """
        First we initialize the wind turbine parameters

        Args:
            D_rotor_array: User input rotor diameter
            Power_rated_array: User input rated power
            hub_height_array: User input hub height
            d: the inflation adjusted discount rate
            AEP: Annual Estimated Production of electricity
            ISO: Alpha-3 code of the country in which the wind turbine is located in

        Returns:
            self: stores the attributes of the wind turbine within the class
        """
        self.D_rotor_array = D_rotor_array
        self.Power_rated_array = Power_rated_array
        self.hub_height_array = hub_height_array 
        self.ISO = ISO
        self.AEP = AEP
        self.d = d

    def landLease(self):
        """
        In this function the annual cost of leasing the land from a landowner is calculated

        Data about the value of arable land in the EU is taken from a Eurostat database

        Args:
            self: relevant attributes of the wind turbine initialized beforehand
        
        Returns:
            landCost: annual cost of leasing the land
        """
        # Some countries are missing from the database and thus they are sorted out
        if self.ISO in ['AUT', 'BEL', 'DEU', 'PRT', 'ITA', 'GRC', 'CYP', 'SRB', 'TUR', 'GBR', 'CHE', 'NOR', 'ROU', 'POL']:
            currentValue = 199 # Average value of arable land in the EU
        else:
            # Use the pycountry python package to get the ISO-2 code from ISO-3 
            ISO2 = pycountry_convert.country_alpha3_to_country_alpha2(self.ISO)
            # Import the dataset with data on Arable land cost
            arableLand = pd.read_csv(r'C:\Users\maxik\Desktop\ETH\Bachelorarbeit\Code\LCOE_model\databases\apri_lrnt_linear.csv')
            # Limit the dataset only to the wanted country
            arableLand = arableLand[arableLand["geo"] == ISO2]
            # Limit the dataset only to arable land costs
            arableLand = arableLand[arableLand["agriprod"] == "ARA_J0000"]
            # Limit the dataset to values in Euro currency
            arableLand = arableLand[arableLand["unit"] == "EUR_HA"]
            # Limit the dataset to values in the year 2019
            arableLand = arableLand[arableLand["TIME_PERIOD"] == 2019]
            # Get the landCost value for a hectare of arable land
            currentValue = arableLand.iloc[0]["OBS_VALUE"]
            
        # NREL average required land use for MW 34.5 [$/MW] multiplied with the land cost and the rated power
        landLeaseCost = 34.5 * self.Power_rated_array/1000 * currentValue
        return int(landLeaseCost)
       
    def insurance(self):
        """
        This function calculates the annual insurance cost of the wind turbine based on the rated power

        Args:
            self: relevant attributes of the wind turbine initialized beforehand

        Returns:
            insuranceCost: annual insurance costs in 2019 USD
        """
        # Projected value of insurance costs for the UK converted with average 2020 exchange rate to USD (1.2809 USD/GBP)
        mottProjection = 37 * 1.2809 # [USD/kW]
        # We need to adjust the value from 2020 to 2019 to work in the same currency
        # Use the world database to get the CPI (Consumer Price Index) from the year 2019
        currentCPI = wb.data.get(['FP.CPI.TOTL'], "GBR", 2019)
        # Use the world database to get the CPI (Consumer Price Index) from the year when the wage was recorded
        pastCPI = wb.data.get(['FP.CPI.TOTL'], "GBR", 2020)
        # Usind the formula we can convert the value from the past wage to the current one
        mottProjection = mottProjection * currentCPI.get('value') / pastCPI.get('value')
        insuranceCost = mottProjection * self.Power_rated_array
        return int(insuranceCost)

    def transmission(self):    
        """
        This function calculates the cost related to the injection of electricity into the grid
        Most countries in Europe do not charge a fee, but in several other countries this can add to the cost

        Args:
            self: relevant attributes of the wind turbine initialized beforehand

        Returns:
            transmissionCost: cost of feeding in the produced electricity into the power grid
        """
        # We sort out the countries in which the electricity provider has to pay a transmission fee
        if self.ISO in ['DEU', 'FIN', 'NOR', 'IRL', 'LVA', 'ROU', 'PRT', 'SVK', 'SWE', 'ESP']:
            # Read the dataset with 2019 values
            dataset = pd.read_csv(r'C:\Users\maxik\Desktop\ETH\Bachelorarbeit\Code\LCOE_model\databases\transmissionCost.csv')
            dataset[dataset['ISO'] == self.ISO]
            # Get the value of the transmissionCost [EUR/MWh]
            transmissionCost = dataset.iloc[0]['value']
            # With the average EUR to USD exchange rate, we bring the cost to 2019 USD
            transmissionCost = transmissionCost * 1.1201
            # Now we multiply the transmission cost with the AEP to get the overall annual cost
            transmissionCost = transmissionCost * (self.AEP/1000)
            return transmissionCost
        else:
            # No transmissionCost in the other countries
            transmissionCost = 0
            return transmissionCost

    def maintenance(self):
        """
        This function returns the cost of the remaining maintenance and operation costs
        The equations used were developed in the Wind Turbine Design Cost and Scale model from NREL
        Then the value gets inflated to 2019 and adjusted with a wage factor as in CapEx depending on the location 
        Args:
            self: relevant attributes of the wind turbine initialized beforehand

        Returns:
            maintenanceCost: cost of the maintenance and remaining operation costs
        """
        # Annual maintenance cost 
        maintenanceCost = 7 * self.AEP/1000
        # Annual replacement cost
        replacementCost = 10.7 * self.Power_rated_array
        # Total annual O&M cost
        OMCost = maintenanceCost + replacementCost
        # We need to adjust the value from 2006 to 2019 to work in the same currency
        # Use the world database to get the CPI (Consumer Price Index) from the year 2019
        currentCPI = wb.data.get(['FP.CPI.TOTL'], "USA", 2019)
        # Use the world database to get the CPI (Consumer Price Index) from the year when the wage was recorded
        pastCPI = wb.data.get(['FP.CPI.TOTL'], "USA", 2006)
        # Usind the formula we can convert the value from the past wage to the current one
        OMCost = OMCost*currentCPI.get('value')/pastCPI.get('value')
        # Import dataset with hourly wages worldwide
        # (CHANGE FOR NEW USER DEPENDING ON LOCATION OF THE DATASET)
        dat = pd.read_csv(r'C:\Users\maxik\Desktop\ETH\Bachelorarbeit\Code\LCOE_model\databases\wages.csv')
        datISO = pd.read_csv(r'C:\Users\maxik\Desktop\ETH\Bachelorarbeit\Code\LCOE_model\databases\wages.csv')
        dat.sort_values(by="time",ascending=False)
        # We only want the average hourly wage, we assume that the price difference are proportional in each country as in the US
        dat = dat[dat["classif1"]=="OCU_SKILL_TOTAL"]
        datISO = datISO[datISO["classif1"]=="OCU_SKILL_TOTAL"]
        # There is no data in USD for Poland thus we make a tentative exception case
        if self.ISO in ['POL']:
            dat = dat[dat["classif2"] == "CUR_TYPE_USD"]
            dat = dat[dat["ref_area"] == 'USA']
            US_wage = dat.iloc[0]['obs_value']
            # Data for Poland's average hourly wage gets converted into USD for ease of comparison
            datISO = datISO[datISO["classif2"] == "CUR_TYPE_LCU"]
            datISO = datISO[datISO["ref_area"] == self.ISO]
            ISO_wage_LCU = datISO.iloc[0]['obs_value']
            # Using the 2019 average PLN to USD exchange rate of 0.2607 USD/PLN
            ISO_wage = ISO_wage_LCU * 0.2607
        elif self.ISO in ['DNK']:
            dat = dat[dat["classif2"] == "CUR_TYPE_USD"]
            dat = dat[dat["ref_area"] == 'USA']
            US_wage = dat.iloc[0]['obs_value']
            # Data for Denmarks's average hourly wage gets converted into USD for ease of comparison
            datISO = datISO[datISO["classif2"] == "CUR_TYPE_LCU"]
            datISO = datISO[datISO["ref_area"] == self.ISO]
            ISO_wage_LCU = datISO.iloc[0]['obs_value']
            # Using the 2019 average PLN to USD exchange rate of 0.2607 USD/PLN
            ISO_wage = ISO_wage_LCU * 0.1500
        else:
            # For most other countries data in USD is available, so no currency exchange needs to be done
            dat = dat[dat["classif2"] == "CUR_TYPE_USD"]
            dat = dat[dat["ref_area"] == 'USA']
            US_wage = dat.iloc[0]['obs_value']
            datISO = datISO[datISO["classif2"] == "CUR_TYPE_USD"]
            datISO = datISO[datISO["ref_area"] == self.ISO]
            ISO_wage = datISO.iloc[0]['obs_value']
        # Finally a wage factor that describes the fraction of hourly pay at our specified location in comparison to the US is created
        wage_factor = ISO_wage/US_wage

        # The OMCost gets multiplied with the wage_factor to account for difference in pay 
        # and adjusted to the LCOE change from 2006 to 2019
        return int(OMCost * wage_factor)

    def getOPEX(self): 
        """
        This function sums up all of the costs that happen in the O&M stage

        Args:
            self: relevant attributes of the wind turbine initialized beforehand

        Returns:
            opexCost: total annual cost of O&M
        """
        # Sum all of the above defined functions together
        opexCost = OPEX.landLease(self) + OPEX.insurance(self) + OPEX.transmission(self) + OPEX.maintenance(self)
        return(opexCost)
    
    def getOPEXadjusted(self): 
        """
        This function sums up all of the costs that happen in the O&M stage
        The maintenance cost is adjusted with a factor

        Args:
            self: relevant attributes of the wind turbine initialized beforehand

        Returns:
            opexCost: total annual cost of O&M
        """
        # Sum all of the above defined functions together
        opexCost = OPEX.landLease(self) + OPEX.insurance(self) + OPEX.transmission(self) + (40.01/92.3) * OPEX.maintenance(self)
        return(opexCost)
    
