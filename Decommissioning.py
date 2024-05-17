"""
Calculate the cost of decommissioning of the wind turbine based on inputs

The model used was taken from the master thesis 'What goes up must come down' by Pérez and Rickardsson, 2008

In their paper they have proposed five activities, two of which are optional
"""

import pandas as pd
import pycountry_convert
import wbgapi as wb

class EOL():

    def __init__(self, D_rotor_array, Power_rated_array, hub_height_array, ISO, n_t):
        """
        First we initialize the wind turbine parameters

        Args:
            D_rotor_array: User input rotor diameter
            Power_rated_array: User input rated power
            hub_height_array: User input hub height
            ISO: Alpha-3 code of the country in which the wind turbine is located in
            

        Returns:
            self: stores the attributes of the wind turbine within the class
        """
        self.D_rotor_array = D_rotor_array
        self.Power_rated_array = Power_rated_array
        self.hub_height_array = hub_height_array 
        self.ISO = ISO
        self.n_t = n_t

    def activityOne(self):
        """
        In this function the cost of dismantling the turbine is calculated

        ActivityOneCost = transport of crane + setup of crane + dissasembly of crane

        Args:
            self: relevant attributes of the wind turbine initialized beforehand

        Returns:
            ActivityOneCost: cost of the first activity from Pérez and Rickardsson, 2008 
        """
        # Convert ISO3 country code into ISO2
        ISO2 = pycountry_convert.country_alpha3_to_country_alpha2(self.ISO)
        # Capacity of the crane 
        craneCapacity = 500
        # Use the dataset for distance and time related transport costs for EU regions from the European Commission
        # Read the CSV file into a DataFrame
        df = pd.read_csv(r'C:\Users\maxik\Desktop\ETH\Bachelorarbeit\Code\LCOE_model\databases\transport.csv')
        # Filter rows where start_nuts begins with ISO2 and start_nuts and end_nuts start with the same two letters (only transport within country)
        filtered_df = df[(df['start_nuts'].str.startswith(ISO2)) & (df['start_nuts'].str[:2] == df['end_nuts'].str[:2])].copy()
        # Calculate the absolute difference between distance_road and 300
        filtered_df.loc[:, 'distance_difference'] = abs(filtered_df['distance_road'] - 300)
        # Find the row with the smallest difference, closest value to the 300 km proposed in the paper
        rentalFee = filtered_df.loc[filtered_df['distance_difference'].idxmin()]
        # Get the total cost associated with this value
        rentalFee = rentalFee.get("total_cost")
        # Initial cost for a crane setup in 2008 Euros
        initialSetupCost = 300000 / 9.6152 
        # The transportation cost for the crane is calculated in 2020 Euros
        transportCost = ((craneCapacity - 200) * (2/50) + 1) * rentalFee
        # The total cost of the crane setup in 2008 Euros
        setupCost = (initialSetupCost * (1 + (2/3) * (self.n_t - 1))) / self.n_t
        # The cost of the dissasembly of the turbine in 2008 Euros
        dissasemblyCost = (5 * (craneCapacity - 200) + 5000) * 8 / (self.n_t * 9.6152)
        # The cost have to be inflation-adjusted and brought to the same year in Sweden
        currentCPI = wb.data.get(['FP.CPI.TOTL'], "SWE", 2019)
        pastCPI = wb.data.get(['FP.CPI.TOTL'], "SWE", 2008)
        futureCPI = wb.data.get(['FP.CPI.TOTL'], "SWE", 2020)
        # Transform the values into the year 2019
        transportCost = transportCost * currentCPI.get('value') / futureCPI.get('value')
        setupCost = setupCost * currentCPI.get('value') / pastCPI.get('value')
        dissasemblyCost = dissasemblyCost * currentCPI.get('value') / pastCPI.get('value')
        # Total cost for activityOne
        activityOneCost = transportCost + setupCost + dissasemblyCost
        # Convert from Euros to $ using the average 2019 exchange rate
        activityOneCost = 1.1201 * activityOneCost
        return int(activityOneCost)
    
    def activityTwo(self):
        """
        In this function the cost of treating the blades is calculated

        ActivityTwoCost = severing of blades + disposal of blades

        Args:
            self: relevant attributes of the wind turbine initialized beforehand

        Returns:
            ActivityTwoCost: cost of the second activity from Pérez and Rickardsson, 2008 
        """
        # Convert ISO3 country code into ISO2
        ISO2 = pycountry_convert.country_alpha3_to_country_alpha2(self.ISO)
        # Weight of blade in tons
        bladeWeight = (3 * 0.1452 * (self.D_rotor_array / 2)**2.9158) / 1000
        # Severing fees Swedisch kronen per tonne 
        severingFee = 150
        # Convert the fees into 2008 Euros using average value
        severingFee = severingFee / 9.6152
        # Adjust the servering fee into 2019 Euros
        currentCPI = wb.data.get(['FP.CPI.TOTL'], "SWE", 2019)
        pastCPI = wb.data.get(['FP.CPI.TOTL'], "SWE", 2008)
        severingFee = severingFee * currentCPI.get('value') / pastCPI.get('value')
        # Disposal fee in 2012 Euros per tonne
        # Use the dataset for landfill costs in EU regions from the European Environment Agency
        # Read the CSV file into a DataFrame
        df = pd.read_csv(r'C:\Users\maxik\Desktop\ETH\Bachelorarbeit\Code\LCOE_model\databases\landfillCost.csv')
        df = df[df["ISO2"] == ISO2]
        disposalFee = df.iloc[0]["total_charge"]
        # Adjust disposalFee to 2019 Euros
        currentCPI = wb.data.get(['FP.CPI.TOTL'], self.ISO, 2019)
        pastCPI = wb.data.get(['FP.CPI.TOTL'], self.ISO, 2012)
        disposalFee = disposalFee * currentCPI.get('value') / pastCPI.get('value')
        # Cost of severing the blades
        severingCost = bladeWeight * severingFee
        # Cost of disposal of the blades in landfills/incineration
        disposalCost = bladeWeight * disposalFee
        # Total cost for activityTwo
        activityTwoCost = severingCost + disposalCost
        # Convert from Euros to $ using the average 2019 exchange rate
        activityTwoCost = 1.1201 * activityTwoCost
        return int(activityTwoCost)
    
    def activityThree(self):
        """
        In this function the cost of treating the tower and nacelle is calculated

        ActivityThreeCost = severing of tower and nacelle - disposal of metal + disposal of organic material

        Args:
            self: relevant attributes of the wind turbine initialized beforehand

        Returns:
            ActivityThreeCost: cost of the third activity from Pérez and Rickardsson, 2008
        """
        # Convert ISO3 country code into ISO2
        ISO2 = pycountry_convert.country_alpha3_to_country_alpha2(self.ISO)
        # Metal weight in tower in tonnes
        metalTower = 66 * (self.Power_rated_array / 1000)
        # Metal weight in nacelle in tonnes
        metalNacelle = 17 * (self.Power_rated_array / 1000)
        # Metal weight in rotor in tonnes
        metalRotor = 4.8 * (self.Power_rated_array / 1000)
        # Nacelle weight in tonnes
        nacelle_cost = 11.537 * self.Power_rated_array + 3849.7
        weightNacelle = nacelle_cost / (10 * 1000)
        # Blade weight in tonnes
        weightBlade = (3 * 0.1452 * (self.D_rotor_array / 2)**2.9158) / 1000
        # Severing fees Swedisch kronen per tonne 
        severingFee = 200
        # Convert the fees into 2008 Euros using average value
        severingFee = severingFee / 9.6152
        # Adjust the severing fee into 2019 Euros
        currentCPI = wb.data.get(['FP.CPI.TOTL'], "SWE", 2019)
        pastCPI = wb.data.get(['FP.CPI.TOTL'], "SWE", 2008)
        severingFee = severingFee * currentCPI.get('value') / pastCPI.get('value')
        # Disposal fee in 2012 Euros per tonne
        # Use the dataset for landfill costs in EU regions from the European Environment Agency
        # Read the CSV file into a DataFrame
        df = pd.read_csv(r'C:\Users\maxik\Desktop\ETH\Bachelorarbeit\Code\LCOE_model\databases\landfillCost.csv')
        df = df[df["ISO2"] == ISO2]
        disposalFee = df.iloc[0]["total_charge"]
        # Adjust disposalFee to 2019 Euros
        currentCPI = wb.data.get(['FP.CPI.TOTL'], self.ISO, 2019)
        pastCPI = wb.data.get(['FP.CPI.TOTL'], self.ISO, 2012)
        disposalFee = disposalFee * currentCPI.get('value') / pastCPI.get('value')
        # Price of metal (steel) per tonne in $
        metalPrice = 783
        # Price of stainless steel per tonne in $
        stainPrice = 1.5 * metalPrice
        # Price of copper per tonne in $
        copperPrice = 9790.50
        # Severing cost for tower, nacelle and rotor
        severingCost = (metalTower + metalNacelle + metalRotor) * severingFee
        # Revenue for disposal of metalTower (Selling it on the world market)
        towerRevenue = 0.9 * metalPrice * metalTower
        # Revenue for disposal of Nacelle (Selling it on the world market)
        nacelleRevenue = weightNacelle * 0.1 * stainPrice + weightNacelle * 0.1 * 0.2 * copperPrice + 0.7 * (weightNacelle * (1 - 0.1 - 0.1 * 0.2)) * metalPrice
        # Revenue for the rotor
        rotorRevenue = weightBlade * 0.9 * metalPrice
        # Cost of organic waste management
        organicCost = 0.1 * metalTower * disposalFee
        # Total revenue for the turbine scraping
        disposalRevenue = towerRevenue + nacelleRevenue + rotorRevenue
        # Two costs are still in Euros and have to be converted into $
        activityThreeCost = (severingCost + organicCost) * 1.1201 - disposalRevenue
        return int(activityThreeCost)
    
    def decommissioningCost(self):
        """
        In this function all of the components of the cost of decommissioning get summed together into the total cost
        Then the cost gets converted into the base currency, adjusted to 2019's level and adjusted to the countrys economic situation

        Args:
            self: relevant attributes of the wind turbine initialized beforehand

        Returns:
            decommissioningCost: total cost of the decommissioning stage in 2019 $

        """
        # Only countries in the EU have data for decommissioning costs
        # For countries outside of the EU the assumption that the scrap value covers the cost of decommissioning is used
        try:
            # The total cost of the decommissioning process is summed from the previous activities
            decommissioningCost = EOL.activityOne(self) + EOL.activityTwo(self) + EOL.activityThree(self)
            # The total cost of decommissioning has to be converted into $ using the 2019 average exchange rate
            decommissioningCost = decommissioningCost * 1.1201
        except:
            decommissioningCost = 0
        return decommissioningCost
