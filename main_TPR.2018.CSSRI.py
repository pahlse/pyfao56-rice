"""
##############################################################################
The main.py module contains the functions and parameters to setup and run
pyfao56 for a hypothtical direct-seede (TPR) rice field at CSSRI Karnal,
Haryana, India for 2018. Weather data is a combination of locally observed IMD
and globaly modeled ISIMIP data. Soil parameters are based on Satyendra et al.
(2019) and crop parameters, planting dates and irrigation scheduling are based
on personal correspondance with local farmers, KVK agronomists and experts.

Plotly is used to generate an interacive plot of relevant WB components in the
CROPWAT 8.0 style. This requires the python plotly library

The main.py module contains the following:
    run - function to setup and run pyfao56 for a hypothetical direct-seeded
          rice field at CSSRI Karnal

13/12/2024 Scripts developed for running pyfao56 for 2018 TPR data
##############################################################################
"""

from datetime import datetime, timedelta
import pandas as pd
import os

from src.autoirrigate import AutoIrrigate
from src.irrigation import Irrigation
from src.model import Model
from src.landprep import Landprep
from src.parameters import Parameters
from src.soil_profile import SoilProfile
from src.tools.visualization import Visualization
from src.update import Update
from src.weather import Weather
from src.custom.plots import WBPlot


def savesums(swbdata, filepath='pyfao56.sum'):
    tmstmp = datetime.now()
    timestamp = tmstmp.strftime('%Y-%m-%d %H:%M:%S')
    sdate = swbdata['startDate'].strftime('%Y-%m-%d')
    edate = swbdata['endDate'].strftime('%Y-%m-%d')
    comment = swbdata.get('comment', 'No comments available.')

    ast = '*'*72
    s = ('{:s}\n'
        'pyfao56: FAO-56 Evapotranspiration in Python\n'
        'Seasonal Water Balance Summary\n'
        'Timestamp: {:s}\n'
        'Simulation start date: {:s}\n'
        'Simulation end date: {:s}\n'
        'All values expressed in mm.\n'
        '{:s}\n'
        '{:s}\n'
        '{:s}\n'
        ).format(ast,timestamp,sdate,edate,ast,comment,ast)

    keys = [ 'ETref', 'ETc', 'ETcadj', 'E', 'T', 'DP', 'K', 'Rain',
            'Runoff', 'Irrig', 'IrrLoss', 'Gross_Irrig', 'Num_Irrig',
            'Mean_Irrig', 'Dr_ini', 'Dr_end', 'Veff_ini', 'Veff_end' ]
    for key in keys:
        value = swbdata.get(key, None)
        if value is not None:
            s += f"{value:8.0f} : {key}\n"
        else:
            s += f"{'N/A':>8} : {key}\n"

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    # Write the summary to the specified file
    with open(filepath, 'w') as file:
        file.write(s)

def run():
    # Get the relevant directories
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    output_dir = os.path.join(os.path.dirname(__file__), "results/2018")

    os.makedirs(os.path.dirname(output_dir), exist_ok=True)

    # Specify the model parameters
    par = Parameters(comment = 'TPR Rice for CSSRI Karnal, 2018')

    par.Kcdry = 0.35
    par.Kcwet = 0.90
    par.Kcbini = 0.15
    par.Kcbmid = 0.95
    par.Kcbend = 0.75
    par.Lnrs = 30
    par.Lini = 30
    par.Ldev = 45
    par.Lmid = 25
    par.Lend = 20
    par.Lprp = 6
    par.Puddays = 4
    par.hini = 0.05
    par.hmax = 1.1
    par.thetaFC = 0.2373
    par.thetaWP = 0.1142
    par.theta0 = 0.0555
    par.thetaS = 0.3725
    par.Ksat = 49
    par.Zrini = 0.4
    par.Zrmax = 0.4
    par.Zp = 0.4
    par.Bundh = 0.3
    par.Wdpud = 50
    par.pbase = 0.6
    par.Ze = 0.1
    par.REW =10
    par.CN2 = 70

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

    wth.savefile(os.path.join(data_dir,'CSSRI_IMD_daily_2018.wth'))


# ------------------------------------------------------------------------------------- #
# Irrigation Data
# ------------------------------------------------------------------------------------- #
    # Specify the planting date
    transplanting_date = '2018-06-01'

    # Convert planting date to a datetime object
    transplanting_datetime = datetime.strptime(transplanting_date, '%Y-%m-%d')
    planting_datetime = transplanting_datetime - timedelta(days=par.Lnrs)
    landprep_datetime = transplanting_datetime - timedelta(days=par.Lprp)

    total_growth_days = par.Lini + par.Ldev + par.Lmid + par.Lend
    harvest_datetime = transplanting_datetime + timedelta(days=total_growth_days)
    irrig_cutoff = harvest_datetime - timedelta(days=14)

    # Convert planting and harvest dates to YYYY-DOY format
    transplanting_doy = transplanting_datetime.strftime('%Y-%j')
    planting_doy = planting_datetime.strftime('%Y-%j')
    landprep_doy =  landprep_datetime.strftime('%Y-%j')
    harvest_doy = harvest_datetime.strftime('%Y-%j')
    irrig_cutoff_doy = irrig_cutoff.strftime('%Y-%j')

    airr = AutoIrrigate()
    airr.addset(transplanting_doy, irrig_cutoff_doy, 
                # mad=0.2, 
                # madDs=0.8,
                madVp=10.0,    #[mm]
                wdpth=70,    #[mm]
                # fpday=1, # Forcasting days 
                # fpdep=1, # Forcasting for forcasting precipitation depth
                # fpact='cancel', # What to do if forcast sais rain
                dsli=3,  # Days since last irrigation event
                dsle=3,  # Days since last watering event
                # evnt=20, # Minimum depth of percip and irr to be considered a watering event (float, mm)
                # icon=70,
                ieff=100)

# ------------------------------------------------------------------------------------- #
# Landprep Simulation
# ------------------------------------------------------------------------------------- #

    ldp = Landprep(landprep_doy, transplanting_doy, par, wth)

    ldp.run()

    columns = ['Date','Year','DOY','DOW','Day','ETref',
               'ETc','ETcadj','T','E','p','Ks','h','Zr',
               'fc','tKcb','Kcb','Kcmax','Kc','Kcadj','Ke','Kr','fw',
               'few','De','DPe','Irrig','IrrLoss','Rain',
               'Runoff','DP','TAW','DAW','RAW','Veff','Vp',
               'Vs','Vr','Ds','Dr','fDr', 'fDs', 'theta0','Se','K']

    ldp_results = ldp.odata
    ldp_df = pd.DataFrame(ldp_results, columns=columns)

    # Update soil parameters after landprep
    par.theta0 = ldp_df.iloc[-1]['theta0']
    par.Wdpud = ldp_df.iloc[-1]['Vp']
    par.Ksat = ldp_df.iloc[-1]['K']

    ldp.savesums(os.path.join(output_dir,f'TPR.LDP.2018.CSSRI.sum'))
    ldp.savefile(os.path.join(output_dir,f'TPR.LDP.2018.CSSRI.out'))

# ------------------------------------------------------------------------------------- #
# Main Simulation
# ------------------------------------------------------------------------------------- #

    #Run the model
    mdl = Model(transplanting_doy, harvest_doy, par, wth, 
                # irr=irr,
                autoirr=airr, 
                ponded=True, 
                puddled=True,
                cons_p=True,
                # aq_Ks=True, 
                comment = '2018 TPR -- CSSRI, Karnal')

    mdl.run()

    mdl.savesums(os.path.join(output_dir,f'TPR.MDL.2018.CSSRI.sum'))
    mdl.savefile(os.path.join(output_dir,f'TPR.MDL.2018.CSSRI.out'))

# ------------------------------------------------------------------------------------- #
# Combine Results
# ------------------------------------------------------------------------------------- #

    mdl_results = mdl.odata
    mdl_df = pd.DataFrame(mdl_results, columns=columns)

    # Align columns and combine results
    ldp_df = ldp_df.reindex(columns=columns)  # Add missing columns, filled with NaN
    mdl_df = mdl_df.reindex(columns=columns)  # Ensure the same column order

    ldp_df['Day'] = range(-len(ldp_df), 0) # reverse the day count order

    df = pd.concat([ldp_df, mdl_df], ignore_index=True)

    required_columns = ['Day', 'Rain', 'Irrig', 'Runoff', 'DP', 'TAW', 'DAW', 'RAW', 'Dr', 'Ds', 'Vp']
    plotly_fig = WBPlot(df)
    plotly_fig.show()

    # Assuming your dataframe is called `df`
    df['Date'] = pd.to_datetime(df['Date'])  # Ensure 'Date' is a datetime object

    # Define start and end dates for the seasonal data
    start_date = df['Date'].min()
    end_date = df['Date'].max()
    start_doy = start_date.strftime("%Y-%j")
    end_doy = end_date.strftime("%Y-%j")

    # Calculate water balance data
    swbdata = {
        'startDate': start_date,
        'endDate': end_date,
        'comment': '2018 TPR -- CSSRI, Karnal',
        'ETref': df['ETref'].sum(),
        'ETc': df['ETc'].sum(), 
        'ETcadj': df['ETcadj'].sum(), 
        'E': df['E'].sum(), 
        'T': df['T'].sum(), 
        'DP': df['DP'].sum(), 
        'K': df['K'].mean(), 
        'Rain': df['Rain'].sum(), 
        'Runoff': df['Runoff'].sum(), 
        'Irrig': df['Irrig'].sum(), 
        'IrrLoss': df['IrrLoss'].sum(), 
        'Gross_Irrig': df['Irrig'].sum() + df['IrrLoss'].sum(), 
        # 'Gross_Irrig': df['Irrig'].sum() + df['IrrLoss'].sum(), 
        'Num_Irrig': len(df[df['Irrig'] > 0]), 
        'Mean_Irrig': df[df['Irrig'] > 0]['Irrig'].mean(), 
        'Dr_ini': df.loc[df['Date'] == start_date, 'Dr'].iloc[0], 
        'Dr_end': df.loc[df['Date'] == end_date, 'Dr'].iloc[0], 
        'Veff_ini': df.loc[df['Date'] == start_date, 'Veff'].iloc[0], 
        'Veff_end': df.loc[df['Date'] == end_date, 'Veff'].iloc[0], 
    }

    savesums(swbdata, filepath=os.path.join(output_dir,f'TPR_2018_CSSRI.sum'))


if __name__ == '__main__':
   run()
