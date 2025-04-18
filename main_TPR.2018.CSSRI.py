"""
##############################################################################
The main.py module contains the functions and parameters to setup and run
pyfao56 for a hypothtical puddled transplanted (TPR) rice field at CSSRI Karnal,
Haryana, India for 2018. Weather data is a combination of locally observed IMD
and globaly modeled ISIMIP data. Soil parameters are based on Kumar et al.
(2019) and crop parameters, planting dates and irrigation scheduling are based
on personal correspondance with local farmers, KVK agronomists and IRRI-ISARC
Scientists.

Plotly is used to generate an interacive plot of relevant WB components in the
CROPWAT 8.0 style. This requires the python plotly library

The main.py module contains the following:
    run - function to setup and run pyfao56 for a hypothetical direct-seeded
          rice field at CSSRI Karnal

13/12/2024 Scripts developed for running pyfao56 for 2018 TPR data
##############################################################################
"""

from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timedelta, date
from threading import Thread
import time
import pandas as pd
import plotly.graph_objects as go
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

def run(base_dir, year, season, month_day, irrig, wdpth):
    # Get the relevant directories
    output_dir = os.path.join(base_dir, str(year))

    # Specify the model parameters
    par = Parameters(comment = 'TPR Rice for CSSRI Karnal, 2018')

    par.Kcbini = 0.15
    par.Kcbmid = 1.15
    par.Kcbend = 0.55
    par.Lini = round(0.25 * season, 0)
    par.Ldev = round(0.375 * season, 0)
    par.Lmid = round(0.2083 * season, 0)
    par.Lend = round(0.1666 * season, 0)
    par.hini = 0.05
    par.hmax = 1.1
    par.thetaFC = 0.276032
    par.thetaWP = 0.153879
    par.theta0 = par.thetaWP # Cannot be lower than thetaWP because of code limitations
    par.thetaR = 0.095234
    par.thetaS = 0.362040
    par.Ksat = 32.080715
    par.Bundh = 0.3
    par.pbase = 0.2
    par.Ze = 0.1
    par.REW = 6 # Based on Table 19; p 144; FAO 56
    par.CN2 = 70

    par.Lprp = 6
    par.Puddays = 4
    par.Zrmax = 0.5
    par.Zrini = par.Zrmax
    par.Zp = 0.5
    par.Wdpud = 50
    theta0_orig = par.theta0 # helper variable to store original theta0


# ------------------------------------------------------------------------------------- #
# Weather Data
# ------------------------------------------------------------------------------------- #

    # Specify the weather data
    wth = Weather(comment = 'CSSRI Karnal 2018\nSource:   IMD & ISIMIP')
    wth.z = 252.64987
    wth.lat = 29.707983
    wth.wndht = 2

    # Import weather data from csv
    weather_data = pd.read_csv("./data/CSSRI_daily_weather_ET0.csv")

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


# ------------------------------------------------------------------------------------- #
# Irrigation Data
# ------------------------------------------------------------------------------------- #
    # Specify the planting date
    transplanting_date = f'{year}-{month_day}'

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
    if irrig > 1:
        madDs = 0
        airr.addset(transplanting_doy, irrig_cutoff_doy, 
                madVp=irrig,    #[mm]
                wdpth=wdpth,    #[mm]
                # fpday=1, # Forcasting days 
                # fpdep=1, # Forcasting for forcasting precipitation depth
                # fpact='cancel', # What to do if forcast says rain
                dsli=2,  # Days since last irrigation event
                dsle=2,  # Days since last watering event
                # evnt=20, # Minimum depth of percip and irr to be considered a watering event (float, mm)
                # icon=70,
                ieff=100)
    else:
        madVp = 0
        airr.addset(transplanting_doy, irrig_cutoff_doy, 
                madDs=irrig,
                wdpth=wdpth,    # Refill to mm over sat
                # fpday=1, # Forcasting days 
                # fpdep=1, # Forcasting for forcasting precipitation depth
                # fpact='cancel', # What to do if forcast says rain
                dsli=2,  # Days since last irrigation event
                dsle=2,  # Days since last watering event
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

    ldp.savesums(os.path.join(base_dir,f'TPR.LDP.{year}.CSSRI.sum'))
    ldp.savefile(os.path.join(base_dir,f'TPR.LDP.{year}.CSSRI.out'))

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

    mdl.savesums(os.path.join(base_dir,f'TPR.MDL.{year}.CSSRI.sum'))
    mdl.savefile(os.path.join(base_dir,f'TPR.MDL.{year}.CSSRI.out'))

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

#---------------------------------
    # plotly_fig = WBPlot(df)
    # plotly_fig.show()

    # Assuming your dataframe is called `df`
    df['Date'] = pd.to_datetime(df['Date'])  # Ensure 'Date' is a datetime object

    # Define start and end dates for the seasonal data
    start_date = df['Date'].min()
    end_date = df['Date'].max()
    start_doy = start_date.strftime("%Y-%j")
    end_doy = end_date.strftime("%Y-%j")

    # Calculate water balance data
    swbdata = {
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
        'IrrLoss': 0.0,
        'Gross_Irrig': df['Irrig'].sum() + df['Irrig'].sum() * 0.3, 
        # 'Gross_Irrig': df['Irrig'].sum() + df['IrrLoss'].sum(), 
        'Num_Irrig': len(df[df['Irrig'] > 0]), 
        'Mean_Irrig': df[df['Irrig'] > 0]['Irrig'].mean(), 
        'Veff_ini': 1000 * (theta0_orig - par.thetaWP) * par.Zrini,
        'Veff_end': df.loc[df['Date'] == end_date, 'Veff'].iloc[0], 
    }

    # savesums(swbdata, filepath=os.path.join(output_dir,f'TPR_2018_CSSRI.sum'))

    summary_data = swbdata
    summary_data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    summary_data['Year'] = year  # Add the year for reference
    summary_data['Transplanting_Date'] = transplanting_date
    if irrig >= 1:
        irrig_crit_value = irrig
        irrig_crit_source = 'madVp'
    else:
        irrig_crit_value = irrig
        irrig_crit_source = 'madDs'

    summary_data['Season'] = season
    summary_data['Irrig_Crit'] = irrig_crit_value
    summary_data['Irrig_Crit_Source'] = irrig_crit_source

    # Reorder the dictionary to have specific keys first
    ordered_summary_data = {
        'timestamp': summary_data['timestamp'],
        'Year': summary_data['Year'],
        'Season': summary_data['Season'],
        'Transplanting_Date': summary_data['Transplanting_Date'],
        'Irrig_Crit_Source': summary_data['Irrig_Crit_Source'],  # Store the source of Irrig_Crit
        'Irrig_Crit': summary_data['Irrig_Crit']
    }

    # Add the rest of the original dictionary
    for key in summary_data:
        if key not in ordered_summary_data:
            ordered_summary_data[key] = round(summary_data[key],2)

    return pd.DataFrame([ordered_summary_data])


    fig = go.Figure()

    # Add traces (lines) for each of the variables: Kcadj, Ke, Kcb, Kcmax
    fig.add_trace(go.Scatter(x=df['Day'], y=df['Kcadj'], mode='lines', name='Kcadj', line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=df['Day'], y=df['Ke'], mode='lines', name='Ke', line=dict(color='lightblue')))
    fig.add_trace(go.Scatter(x=df['Day'], y=df['Kcb'], mode='lines', name='Kcb', line=dict(color='darkgreen')))
    fig.add_trace(go.Scatter(x=df['Day'], y=df['Kcmax'], mode='lines', name='Kcmax', line=dict(color='gray')))

    # Update layout to add labels and title
    fig.update_layout(
        title="Time Series of Kcadj, Ke, Kcb, and Kcmax",
        xaxis_title="Day",
        yaxis_title="Coefficient Values",
        legend_title="Legend",
        xaxis=dict(
            tickmode='linear',  # Linear mode for custom ticks
            dtick=5             # Tick interval of 5 days
        ),
        legend=dict(x=0.5, xanchor='center', y=1.1, orientation='h'),  # Legend positioning
        template='plotly_white'  # Clean background
    )

    # fig.show()


def run_simulations(base_dir, years_to_simulate, seasons, month_days, irrigation_crit, irrigation_levels):
    start_time = time.time()
    all_summary_data = []  # List to collect all DataFrames

    # Using ProcessPoolExecutor for parallel execution
    with ProcessPoolExecutor(max_workers=8) as executor:  # You can adjust the number of workers
        futures = []

        total_simulations = len(years_to_simulate) * len(seasons) * len(month_days) * len(irrigation_crit)
        current_simulation = 0       

        # Loop over the combinations of seasons, month_days, irrigation_crit, and years
        for season in seasons:
            for month_day in month_days:
                for irrig_crit_value in irrigation_crit:
                    for year in years_to_simulate:
                        # Submit the task to the executor
                        futures.append(executor.submit(run, base_dir, year, season, month_day, irrig_crit_value, irrigation_levels))
                        

        # Collect the results from each completed task
        for future in as_completed(futures):
            summary_df = future.result()
            all_summary_data.append(summary_df)  # Add the returned DataFrame to the list
            current_simulation += 1  # Increment the simulation counter
            elapsed_time = time.time() - start_time
            minutes = int(elapsed_time // 60)
            seconds = int(elapsed_time % 60)
            print(f"\r[{minutes:02}:{seconds:02}] Simulation {current_simulation}/{total_simulations}", end='', flush=True)

    
    # Concatenate all collected DataFrames into one final DataFrame
    return pd.concat(all_summary_data, ignore_index=True)
    

def main():
    # Setup directories and simulation parameters
    datestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    base_dir = "./results/"
    os.makedirs(base_dir, exist_ok=True)

    # years_to_simulate = range(1989, 2020)  # Example years
    # seasons = [120, 135, 145]
    # month_days = ['05-15', '06-01', '06-15', '07-01', '07-15']
    # irrigation_crit = [50, 10, 0.47, 0.75] # mm madVs/Ds NOTE: may not be 0! will break if condition above

    years_to_simulate = [2017]  # Example years
    seasons = [120]
    month_days = ['07-01']
    irrigation_crit = [0.75] # mm madVs/Ds NOTE: may not be 0! will break if condition above

    irrigation_levels = 70 #[mm] 

    # Run simulations and collect results
    final_df = run_simulations(base_dir, years_to_simulate, seasons, month_days, irrigation_crit, irrigation_levels)

    # Save the final DataFrame to CSV
    final_csv_path = os.path.join(base_dir, f'TPR_{datestamp}.csv')
    final_df.to_csv(final_csv_path, index=False)
    print(f"\nConsolidated summary saved to {final_csv_path}")


if __name__ == '__main__':
    main()
