"""
##############################################################################
The main.py module contains the functions and parameters to setup and run
pyfao56 for a hypothtical direct-seede (DSR) rice field at CSSRI Karnal,
Haryana, India for 2018. Weather data is a combination of locally observed IMD
and globaly modeled ISIMIP data. Soil parameters are based on Satyendra et al.
(2019) and crop parameters, planting dates and irrigation scheduling are based
on personal correspondance with local farmers, KVK agronomists and experts.

Plotly is used to generate an interacive plot of relevant WB components in the
CROPWAT 8.0 style. This requires the python plotly library

The main.py module contains the following:
    run - function to setup and run pyfao56 for a hypothetical direct-seeded
          rice field at CSSRI Karnal

13/12/2024 Scripts developed for running pyfao56 for 2018 DSR data
##############################################################################
"""

from datetime import datetime, timedelta
import pandas as pd
import os

from src.autoirrigate import AutoIrrigate
from src.irrigation import Irrigation
from src.model import Model
from src.parameters import Parameters
from src.soil_profile import SoilProfile
from src.update import Update
from src.weather import Weather
from src.custom.plots import WBPlot

def run():
    """Setup and run pyfao56 as a test"""

    # Get the relevant directory
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    output_dir = os.path.join(os.path.dirname(__file__), "results")

    # Specify the model parameters
    par = Parameters(comment = 'DSR Rice for CSSRI Karnal, 2018')

    par.Kcbini = 0.9
    par.Kcbmid = 1.42
    par.Kcbend = 0.91
    par.Lini = 30
    par.Ldev = 45
    par.Lmid = 25
    par.Lend = 20
    par.hini = 0.05
    par.hmax = 1.1
    par.thetaFC = 0.2373
    par.thetaWP = 0.1142
    par.theta0 = 0.0655
    par.thetaS = 0.3725
    # par.Ksat = 40.9243
    par.Ksat = 40.9243**0.33 #According to CROPWAT 8.0 this is Ksat after puddling
    par.Zrini = 0.2
    par.Zrmax = 0.6
    par.Bundh = 0.3
    par.Wdini = 70 #This does not yet do anything; the idea is to define a initial water depth at transplanting
    par.pbase = 0.6
    par.Ze = 0.1
    par.REW =10
    par.CN2 = 70

    par.savefile(os.path.join(data_dir,'CSSRI_DSR_2018.par'))


# ------------------------------------------------------------------------------------- #
# Weather Data
# ------------------------------------------------------------------------------------- #

    # Specify the weather data
    wth = Weather(comment = 'CSSRI Karnal 2018\nSource:   IMD & ISIMIP')
    wth.z = 252.64987
    wth.lat = 29.707983
    wth.wndht = 2

    # Import weather data from csv
    weather_data = pd.read_csv(os.path.join(data_dir, "CSSRI_IMD_daily_2018.csv"))

    # Convert the 'date' column to datetime and extract year and day of year
    if 'DATE' in weather_data.columns:
        weather_data['DATE'] = pd.to_datetime(weather_data['DATE'], format='%Y-%m-%d')
        weather_data['YEAR'] = weather_data['DATE'].dt.year
        weather_data['DOY'] = weather_data['DATE'].dt.strftime('%j')

    # Create a list of required columns in the correct order
    required_columns = ['Srad', 'Tmax', 'Tmin', 'Vapr', 'Tdew', 'RHmax', 'RHmin',
                        'Wndsp', 'Rain', 'ETref', 'MorP']

    # Create an empty DataFrame with all the required columns filled with NaN
    wth.wdata = pd.DataFrame(columns=required_columns)

    column_mapping = {
        'SRAD': 'Srad',
        'TMAX': 'Tmax',
        'TMIN': 'Tmin',
        'VAPR': 'Vapr',
        'TDEW': 'Tdew',
        'RHMAX': 'RHmax',
        'RHMIN': 'RHmin',
        'WNDSP': 'Wndsp',
        'RAIN': 'Rain',
        'ETREF': 'ETref',
        'MORP': 'MorP'
    }

    for csv_col, wdata_col in column_mapping.items():
        if csv_col in weather_data.columns:
            wth.wdata[wdata_col] = weather_data[csv_col]

    wth.wdata['MorP'] = 'M'

    wth.wdata.index = weather_data['YEAR'].astype(str) + '-' + weather_data['DOY']

    # wth.loadfile(os.path.join(data_dir,'cotton2018.wth'))

    etref_list = []

    # for index in wth.wdata.index:
    #     etref_list.append(wth.compute_etref(index))

    # wth.wdata['ETref'] = etref_list

    wth.savefile(os.path.join(data_dir,'CSSRI_IMD_daily_2018.wth'))
    # wth.loadfile(os.path.join(data_dir,'CSSRI_IMD_daily_2018.wth'))



# ------------------------------------------------------------------------------------- #
# Irrigation Data
# ------------------------------------------------------------------------------------- #
    # Specify the planting date
    planting_date = '2018-06-01'

    # Convert planting date to a datetime object
    planting_datetime = datetime.strptime(planting_date, '%Y-%m-%d')
    total_growth_days = par.Lini + par.Ldev + par.Lmid + par.Lend
    harvest_datetime = planting_datetime + timedelta(days=total_growth_days)

    # Convert planting and harvest dates to YYYY-DOY format
    planting_doy = planting_datetime.strftime('%Y') + '-' + planting_datetime.strftime('%j')
    harvest_doy = harvest_datetime.strftime('%Y') + '-' + harvest_datetime.strftime('%j')

    # Specify the irrigation schedule
    irr = Irrigation(comment = 'DSR 2018 -- CSSRI, Karnal')
    irr.addevent(2018, 152, 70.0, 1)
    irr.addevent(2018, 162, 70.0, 1)
    irr.addevent(2018, 172, 70.0, 1)
    irr.addevent(2018, 232, 220.0, 1)

    # irr.savefile(os.path.join(data_dir,'CSSRI_DSR_2018.irr'))
    # irr.loadfile(os.path.join(module_dir,'cottondry2013.irr'))

    airr = AutoIrrigate()
    airr.addset(planting_doy, '2018-252', 
                # mad=0.5, 
                madDs=0.01,
                # madVp=10.0,    #[mm]
                # wdpth=100,    #[mm]
                fpday=1, 
                fpdep=1, 
                fpact='cancel', 
                dsli=5, 
                dsle=5, 
                ieff=100)

    # airr.savefile(os.path.join(output_dir,'CSSRI_DSR_2018.air'))


# ------------------------------------------------------------------------------------- #
# Call the Model
# ------------------------------------------------------------------------------------- #

    #Run the model
    mdl = Model(planting_doy, harvest_doy, par, wth, 
                # irr=irr,
                autoirr=airr, 
                # roff=True,  #NOTE: Runoff not working for now. There is a bug!!!
                ponded=True, 
                cons_p=False, 
                aq_Ks=True, 
                comment = '2018 DSR -- CSSRI, Karnal')

    mdl.run()

    # Save the model results
    mdl.savesummary(os.path.join(output_dir,'CSSRI_DSR_2018_test.out'))
    mdl.savesums(os.path.join(output_dir,'CSSRI_DSR_2018_test.sum'))
    mdl.savecsv(os.path.join(output_dir,'CSSRI_DSR_2018_test.csv'))
    print('Model output saved successfully.')

    # # Plot the model results
    required_columns = ['Day', 'Rain', 'Irrig', 'Runoff', 'DP', 'TAW', 'DAW', 'RAW', 'Dr', 'Ds', 'Vp']
    results_mdl = mdl.odata[required_columns]

    plotly_fig = WBPlot(results_mdl)
    plotly_fig.show()


if __name__ == '__main__':
    run()
