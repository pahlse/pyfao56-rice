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
# from src.custom.vangenuchten import vanGenuchten

def run():
    """Setup and run py56 as a test"""

    # Get the relevant directory
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    output_dir = os.path.join(os.path.dirname(__file__), "results")

    # Specify the model parameters
    par = Parameters(comment = '2018 Rice')

    par.Kcbini = 0.9000
    par.Kcbmid = 1.4200
    par.Kcbend = 0.9100
    par.Lini = 30
    par.Ldev = 45
    par.Lmid = 25
    par.Lend = 20
    par.hini = 0.0500
    par.hmax = 1.1000
    par.thetaFC = 0.2373293
    par.thetaWP = 0.1142707
    par.theta0 = 0.0655235463679017
    par.thetaS = 0.3725299447204550
    par.Ksat = 44.924302288007300
    par.Zrini = 0.2000
    par.Zrmax = 0.6000
    par.Bundh = 0.3000
    par.Wdini = 70.000
    par.pbase = 0.6000
    par.Ze = 0.1000
    par.REW =10.0000
    par.CN2 = 70

    par.savefile(os.path.join(data_dir,'CSSRI_DSR_2018.par'))


# ------------------------------------------------------------------------------------- #
# Weather Data
# ------------------------------------------------------------------------------------- #

    # Specify the weather data
    wth = Weather(comment = 'CSSRI Karnal 2018\nSource:   IMD')
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

    # wth.savefile(os.path.join(data_dir,'CSSRI_IMD_daily_2018.wth'))
    wth.loadfile(os.path.join(data_dir,'CSSRI_IMD_daily_2018.wth'))



# ------------------------------------------------------------------------------------- #
# Irrigation Data
# ------------------------------------------------------------------------------------- #
    # Specify the planting date
    planting_date = '2018-05-15'

    # Convert planting date to a datetime object
    planting_datetime = datetime.strptime(planting_date, '%Y-%m-%d')
    total_growth_days = par.Lini + par.Ldev + par.Lmid + par.Lend
    harvest_datetime = planting_datetime + timedelta(days=total_growth_days)

    # Convert planting and harvest dates to YYYY-DOY format
    planting_doy = planting_datetime.strftime('%Y') + '-' + planting_datetime.strftime('%j')
    harvest_doy = harvest_datetime.strftime('%Y') + '-' + harvest_datetime.strftime('%j')

    # Specify the irrigation schedule
    # irr = Irrigation(comment = '2018 Rice -- CSSRI')
    airr = AutoIrrigate()
    airr.addset(planting_doy, harvest_doy, mad=0.8, ieff=70)

    airr.savefile(os.path.join(output_dir,'CSSRI_DSR_2018_test.air'))


# ------------------------------------------------------------------------------------- #
# Call the Model
# ------------------------------------------------------------------------------------- #

    #Run the model
    mdl = Model(planting_doy, harvest_doy, par, wth, autoirr=airr, ponded=True, cons_p=False,
                    comment = '2018 DSR -- CSSRI')

    mdl.run()

    # Save the model results
    mdl.savesummary(os.path.join(output_dir,'CSSRI_DSR_2018_test.out'))
    mdl.savesums(os.path.join(output_dir,'CSSRI_DSR_2018_test.sum'))
    print('Model output saved successfully.')

    # # Plot the model results
    required_columns = ['Day', 'Rain', 'Irrig', 'DP', 'TAW', 'RAW', 'Dr', 'Ds']
    results_mdl = mdl.odata[required_columns]

    # print("odata:", mdl.odata.columns)
    # print("results_mdl:", results_mdl.columns)

    # plotly_fig = WBPlot(results_mdl)
    # plotly_fig.show()


if __name__ == '__main__':
    run()
