"""
########################################################################
The nursery.py module contains the Landprep class, which
provides I/O tools for defining the land preparation stage for paddy rice 
in pyfao56. It tries to replicate the original CROPWAT 8.0 functionalities.

The landprep.py module contains the following:
    LandPrep - A class for managing multiple sets of conditions for
                   nursery establishment.

10/12/2024 Initial Python function developed by Elias Pahls
########################################################################
"""

class LandPrep:
    """A class for managing input parameters for FAO-56 calculations

    Attributes
    ----------
    
    Methods
    ------
    """

    # def __init__(self, Kcbini=0.15, Kcbmid=1.10, Kcbend=0.50, Lini=25,
    #              Ldev=50, Lmid=50, Lend=25, hini=0.010, hmax=1.20,
    #              thetaFC=0.250, thetaWP=0.100, theta0=0.100, thetaS=0.33, 
    #              Ksat=42.0, Zrini=0.20, Zrmax=1.40, pbase=0.50, Ze=0.10, 
    #              REW=8.0, CN2=70, comment=''):
    #     """Initialize the Parameters class attributes.

    #     Default parameter values are given below. Users should update
    #     the parameters with values for their specific crop and field
    #     conditions based on FAO-56 documentation.

    #     Parameters
    #     ----------
    #     See Parameters class docstring for parameter definitions.
    #     """
