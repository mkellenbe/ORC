# ORC (Open-source Regional-specific lCoe model)

This open-source code is used for estimating the Levelized Cost of Electricity for wind turbines dependent on their technical and location-specific data. It is based on the LandBOSSE and Wind Turbine Design Cost and Scaling model from NREL. 

Links to the used models are here found here:

LandBOSSE: https://github.com/WISDEM/LandBOSSE

WTDCSM: https://gitlab.windenergy.dtu.dk/TOPFARM/TopFarm2/-/blob/master/topfarm/cost_models/economic_models/turbine_cost.py?ref_type=heads

The model's tools and their functionality are described shortly in the ORC instructions.ipynb Jupyter notebook. 

BEFORE FIRST USE IT IS IMPORTANT TO CHECK IF ALL DIRECTORIES ARE AS THEY SHOULD BE AND IF THE FILES ARE ACCESSED RIGHT!!

## Three steps are neccessary for the code to work:

1) Create a "output" folder in .\landbosse\ -> .\landbosse\output\

2) Change https://github.com/mkellenbe/ORC/blob/9fb0540066d2921681027f78e426e502fb915886/CapEx.py#L498 to os.system(r"python main.py -i C:(NEW DIRECTORY)\landbosse\input -o C:(NEW DIRECTORY)\landbosse\output, because LandBOSSE is a command line model

3) Change the remaining absolute paths to your own in:
   https://github.com/mkellenbe/ORC/blob/9fb0540066d2921681027f78e426e502fb915886/DiscountRate.py#L90
   https://github.com/mkellenbe/ORC/blob/9fb0540066d2921681027f78e426e502fb915886/CapEx.py#L533
   https://github.com/mkellenbe/ORC/blob/9fb0540066d2921681027f78e426e502fb915886/OpEx.py#L56
   https://github.com/mkellenbe/ORC/blob/9fb0540066d2921681027f78e426e502fb915886/OpEx.py#L108
   https://github.com/mkellenbe/ORC/blob/9fb0540066d2921681027f78e426e502fb915886/OpEx.py#L148
   https://github.com/mkellenbe/ORC/blob/9fb0540066d2921681027f78e426e502fb915886/OpEx.py#L149
   https://github.com/mkellenbe/ORC/blob/9fb0540066d2921681027f78e426e502fb915886/Decommissioning.py#L53
   https://github.com/mkellenbe/ORC/blob/9fb0540066d2921681027f78e426e502fb915886/Decommissioning.py#L111
   https://github.com/mkellenbe/ORC/blob/9fb0540066d2921681027f78e426e502fb915886/Decommissioning.py#L164

   Absolute paths can also be transformed into relative paths in future versions, but there was some trouble with this in the current version, thus the complication.
