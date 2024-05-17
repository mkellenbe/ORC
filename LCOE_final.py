"""
Here the final LCOE calculation with all of the other parts is combined

LCOE = Sum(Total cost/(1+d)^t) / Sum(Total energy produced/(1+d)^t)

d - discount rate, t - year of operation (assuming N=20)

Total cost = CapEx(t) + OpEx(t) + Decommissioning(t) 
"""
# First we import the needed modules
import math
# We import all the cost classes created for cost modeling
from AEP_estimation import AEP
from OpEx import OPEX
from CapEx import CAPEX
from Decommissioning import EOL
from DiscountRate import discountRate
    
class LCOE():

    def __init__(self, D_rotor, Power_rated, hub_height, ISO, n_t, version):
        """
        First we initialize the wind turbine parameters

        Args:
            D_rotor: User input rotor diameter
            Power_rated: User input rated power
            hub_height: User input hub height
            ISO: Alpha-3 code of the country in which the wind turbine is located in

        Returns:
            self: stores the attributes of the wind turbine within the class
        """
        self.D_rotor = D_rotor
        self.Power_rated = Power_rated
        self.hub_height = hub_height 
        self.ISO = ISO
        self.n_t = n_t
        self.version = version

    def getLCOE(self):
        AEPfactor = self.Power_rated / 3370
        AEPvalue = AEP.AEP_sim() * (AEPfactor)

        # The inflation adjusted discount rate gets returned
        d = discountRate.InfAdjRate(self.ISO)

        # We initialize the turbine with the input values needed for each cost component
        TurbineCAPEX = CAPEX(self.D_rotor, self.Power_rated, self.hub_height, self.ISO)
        TurbineOPEX = OPEX(self.D_rotor, self.Power_rated, self.hub_height, d, AEPvalue, self.ISO)
        TurbineDecommissioning = EOL(self.D_rotor, self.Power_rated, self.hub_height, self.ISO, self.n_t)

        # Based on the model version calculate the costs
        if self.version == 'original':
            # The CAPEX cost of the turbine gets returned
            CAPEXcost = CAPEX.getCAPEX(TurbineCAPEX)
            # The annual OPEX cost of the turbine gets returned
            OPEXcost = OPEX.getOPEX(TurbineOPEX) 
        else:
            # The CAPEX cost of the turbine gets returned
            CAPEXcost = CAPEX.getCAPEXadjusted(TurbineCAPEX)
            # The annual OPEX cost of the turbine gets returned
            OPEXcost = OPEX.getOPEXadjusted(TurbineOPEX) 

        # The decommissioning cost of the turbine gets returned
        DecommissioningCost = EOL.decommissioningCost(TurbineDecommissioning)

        # Here the final LCOE calculation gets initialized
        lifetime = 20
        discountedEnergy = 0
        discountedCost = 0
        x = 0
        # The discountedCost and discountedEnergy get calculated
        while x <= lifetime:
            if x == 0:
                # CAPEXcost is added to LCOE equation before the start of operation 
                discountedCost += CAPEXcost
                x = x + 1
            elif x == 20:
                # OPEX costs get discounted and added to the LCOE equation
                discountedCost += (OPEXcost + DecommissioningCost) * 1 / (math.pow((1+d) , x))
                # Same happens to the energy produced annually
                discountedEnergy += (AEPvalue) * (1 / (math.pow((1+d) , x)))
                x = x + 1
            else:
                # OPEX costs get discounted and added to the LCOE equation
                discountedCost += OPEXcost * 1 / (math.pow((1+d) , x)) 
                # Same happens to the energy produced annually
                discountedEnergy += (AEPvalue) * (1 / (math.pow((1+d) , x)))
                x = x + 1
      
        LCOEvalue = (discountedCost/discountedEnergy) * 1000
        return LCOEvalue