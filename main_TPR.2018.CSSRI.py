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

def savesums(combined_df, filepath='./results/combined_results_TPR.sum', comment=''):
    tmstmp = datetime.now()
    timestamp = tmstmp.strftime('%Y-%m-%d %H:%M:%S')
    
    ast = '*' * 72
    s = (f'{ast}\n'
         f'pyfao56: FAO-56 Evapotranspiration in Python\n'
         f'Seasonal Water Balance Summary\n'
         f'Timestamp: {timestamp}\n'
         f'All values expressed in mm.\n'
         f'{ast}\n'
         f'{comment}\n'
         f'{ast}\n')

    if not combined_df.empty:
        # Keys to include in the summary
        keys = [
            'ETref', 'ETc', 'ETcadj', 'E', 'T', 'DP', 'K', 'Rain', 'Runoff',
            'Irrig', 'IrrLoss', 'Gross_Irrig', 'Num_Irrig', 'Mean_Irrig',
            'Dr_ini', 'Dr_end', 'Veff_ini', 'Veff_end'
        ]

        # Aggregate data for the keys
        swbdata = combined_df[keys].sum(axis=0, skipna=True)
        for key in keys:
            if key in swbdata:
                s += f'{swbdata[key]:8.3f} : {key}\n'

    try:
        with open(filepath, 'w') as f:
            f.write(s)
    except FileNotFoundError:
        print('The filepath for summary data is not found.')
    else:
        print(f'Summary saved successfully to {filepath}')

def run():
    """Setup and run pyfao56 as a test"""

    # Get the relevant directory
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    output_dir = os.path.join(os.path.dirname(__file__), "results")

    # Specify the model parameters
    par = Parameters(comment = 'TPR Rice for CSSRI Karnal, 2018')

    par.Kcbnrs = 0.1
    par.Kcdry = 0.35
    par.Kcwet = 1.1
    par.Kcbini = 0.10
    par.Kcbmid = 0.95
    par.Kcbend = 0.72
    par.Lnrs = 30
    par.Lini = 30
    par.Ldev = 45
    par.Lmid = 25
    par.Lend = 20
    par.Lprp = 7
    par.Puddays = 5
    par.hini = 0.05
    par.hmax = 1.1
    par.thetaFC = 0.2373
    par.thetaWP = 0.1142
    par.theta0 = 0.0555
    par.thetaS = 0.3725
    par.Ksat = 8
    par.Zrini = 0.4
    par.Zrmax = 0.4
    par.Zp = 0.4
    par.Bundh = 0.3
    par.Wdpud = 50
    par.pbase = 0.6
    par.Ze = 0.1
    par.REW =10
    par.CN2 = 70

    # par.savefile(os.path.join(data_dir,'CSSRI_TPR_2018.par'))


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

    # Specify the irrigation schedule
    irr = Irrigation(comment = 'TPR 2018 -- CSSRI, Karnal')
    irr.addevent(2018, 152, 70.0, 1)
    irr.addevent(2018, 162, 70.0, 1)
    irr.addevent(2018, 172, 70.0, 1)
    irr.addevent(2018, 232, 220.0, 1)

    # irr.savefile(os.path.join(data_dir,'CSSRI_TPR_2018.irr'))
    # irr.loadfile(os.path.join(module_dir,'cottondry2013.irr'))

    airr = AutoIrrigate()
    airr.addset(transplanting_doy, irrig_cutoff_doy, 
                # mad=0.2, 
                # madDs=0.8,
                madVp=30.0,    #[mm]
                wdpth=70,    #[mm]
                # fpday=1, # Forcasting days 
                # fpdep=1, # Forcasting for forcasting precipitation depth
                # fpact='cancel', # What to do if forcast sais rain
                # dsli=5,  # Days since last irrigation event
                # dsle=5,  # Days since last watering event
                # evnt=20, # Minimum depth of percip and irr to be considered a watering event (float, mm)
                # icon=70,
                ieff=100)

    airr.savefile(os.path.join(output_dir,'CSSRI_TPR_2018.air'))

    
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

    par.theta0 = ldp_df.iloc[-1]['theta0']
    par.Wdpud = ldp_df.iloc[-1]['Vp']
    par.Ksat = ldp_df.iloc[-1]['K']


    print(par.Ksat)

# ------------------------------------------------------------------------------------- #
# Main Simulation
# ------------------------------------------------------------------------------------- #

    #Run the model
    mdl = Model(transplanting_doy, harvest_doy, par, wth, 
                # irr=irr,
                autoirr=airr, 
                # roff=True,  #NOTE: Runoff not working for now. There is a bug!!!
                ponded=True, 
                puddled=True,
                cons_p=True,
                # aq_Ks=True, 
                comment = '2018 TPR -- CSSRI, Karnal')

    mdl.run()

    mdl_results = mdl.odata
    mdl_df = pd.DataFrame(mdl_results, columns=columns)


    # Align columns and combine results
    ldp_df = ldp_df.reindex(columns=columns)  # Add missing columns, filled with NaN
    mdl_df = mdl_df.reindex(columns=columns)  # Ensure the same column order

    ldp_df['Day'] = range(-len(ldp_df), 0)

    combined_df = pd.concat([ldp_df, mdl_df], ignore_index=True)

    # Save combined results to a single file
    output_file = os.path.join(output_dir, 'CSSRI_TPR_2018_combined_results.csv')
    combined_df.to_csv(output_file, index=False)

    # # Save the model results
    # # mdl.savesummary(os.path.join(output_dir,'CSSRI_TPR_2018_summary.out'))
    # mdl.savesums(os.path.join(output_dir,'CSSRI_TPR_2018_test.sum'))
    # # mdl.savecsv(os.path.join(output_dir,'CSSRI_TPR_2018_test.csv'))
    # mdl.savefile(os.path.join(output_dir,'CSSRI_TPR_2018_test.out'))
    # print('Model output saved successfully.')

    # # Plot the model results
    required_columns = ['Day', 'Rain', 'Irrig', 'Runoff', 'DP', 'TAW', 'DAW', 'RAW', 'Dr', 'Ds', 'Vp']
    combined_plot = mdl.odata[required_columns]

    plotly_fig = WBPlot(combined_df)
    plotly_fig.show()

    # vis = Visualization(mdl, dayline=True)
    # vis.plot_Kc(title='2018 PRT p10-2 Kc',
    #             show=True,
    #             filepath=os.path.join(output_dir,'CSSRI_TPR_2018_test.png'))

    def add_sums(mdl_sums, ldp_sums):
        combined_sums = {}
        for key in mdl_sums.keys():
            combined_sums[key] = mdl_sums.get(key, 0) + ldp_sums.get(key, 0)
        return combined_sums

    mdl_sums = mdl.swbdata 
    ldp_sums = ldp.swbdata
    total_sums = add_sums(mdl_sums, ldp_sums)

    # Print the combined sums

    for key, value in total_sums.items():
        print(f"{key}: {value:.3f}")

    savesums(combined_df = total_sums)




if __name__ == '__main__':
   run()
