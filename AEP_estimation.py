from py_wake.examples.data.iea37._iea37 import IEA37_WindTurbines, IEA37Site 
from py_wake.deficit_models.gaussian import IEA37SimpleBastankhahGaussian
from topfarm.examples.iea37 import get_iea37_initial

class AEP():

    def AEP_sim(): 
        n_wt = 16 # number of wind turbines
        site = IEA37Site(n_wt) # site is the IEA Wind Task 37 site with a circle boundary
        windTurbines = IEA37_WindTurbines() # wind turbines are the IEA Wind Task 37 3.4 MW reference turbine
        wake_model = IEA37SimpleBastankhahGaussian(site, windTurbines) # select the Gaussian wake model
        x, y = get_iea37_initial(n_wt).T
        AEPs = wake_model(x, y).aep().sum(['wd','ws']).values*10**6
        AEP = AEPs.sum() / 16 
        return(AEP)

