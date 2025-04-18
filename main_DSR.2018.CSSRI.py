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

from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timedelta
import pandas as pd
import time
from pandas.io.xml import file_exists
import plotly.graph_objects as go
import os

from src.autoirrigate import AutoIrrigate
from src.irrigation import Irrigation
from src.model import Model
from src.parameters import Parameters
from src.soil_profile import SoilProfile
from src.tools.visualization import Visualization
from src.update import Update
from src.weather import Weather
from src.custom.plots import WBPlot

def run(base_dir, year, season, month_day, irrig):

    output_dir = os.path.join(base_dir, str(year))

    # Specify the model parameters
    par = Parameters(comment = 'DSR Rice for CSSRI Karnal')

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
    par.Zrini = 0.2
    par.Zrmax = 0.6
    par.Bundh = 0.3
    par.pbase = 0.2
    par.Ze = 0.1
    par.REW = 6 # Based on Table 19; p 144; FAO 56
    par.CN2 = 70

# ------------------------------------------------------------------------------------- #
# Weather Data
# ------------------------------------------------------------------------------------- #


    # Specify the weather data
    wth = Weather(comment=f'CSSRI Karnal {year}\nSource:   IMD & ISIMIP')
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

    column_mapping = { 'SRAD': 'Srad', 
                      'TMAX': 'Tmax', 
                      'TMIN': 'Tmin', 
                      'VAPR': 'Vapr', 
                      'TDEW': 'Tdew', 
                      'RHMAX': 'RHmax', 
                      'RHMIN': 'RHmin', 
                      'WNDSP': 'Wndsp', 
                      'RAIN': 'Rain', 
                      'ETREF': 'ETref', 
                      'MORP': 'MorP' }

    for csv_col, wdata_col in column_mapping.items():
        if csv_col in weather_data.columns:
            wth.wdata[wdata_col] = weather_data[csv_col]

    wth.wdata['MorP'] = 'M'
    wth.wdata.index = weather_data['YEAR'].astype(str) + '-' + weather_data['DOY']


# ------------------------------------------------------------------------------------- #
# Irrigation Data
# ------------------------------------------------------------------------------------- #
    # Specify the planting date
    planting_date = f'{year}-{month_day}'

    # Convert planting date to a datetime object
    planting_datetime = datetime.strptime(planting_date, '%Y-%m-%d')
    total_growth_days = par.Lini + par.Ldev + par.Lmid + par.Lend
    harvest_datetime = planting_datetime + timedelta(days=total_growth_days)
    irrig_cutoff = harvest_datetime - timedelta(days=14)

    # Convert planting and harvest dates to YYYY-DOY format
    planting_doy = planting_datetime.strftime('%Y-%j')
    harvest_doy = harvest_datetime.strftime('%Y-%j')
    irrig_cutoff_doy = irrig_cutoff.strftime('%Y-%j')

    # madDs=0.47      # irrigate at 10 kPa (float, frac)
    # madDs=0.75      # irrigate at 20 kPa (float, frac)
    # madDs=0.94      # irrigate at 30 kPa (float, frac)
    # madDs=0
    # mad=0.06      # irrigate at 40 kPa (float, frac)

    airr = AutoIrrigate()
    if irrig != 0:
        airr.addset(planting_doy, irrig_cutoff_doy,
                madDs=irrig,
                wdpth=0,    #[mm] refill to sat
                fpday=1, # Forcasting days 
                fpdep=1, # Forcasting for forcasting precipitation depth
                dsli=2,  # Days since last irrigation event
                dsle=2,  # Days since last watering event
                fpact='cancel', # What to do if forcast sais rain
                ieff=100)
    else:
        airr.addset(planting_doy, irrig_cutoff_doy,
                mad=0.06,
                wdpth=0,    #[mm]
                fpday=1, # Forcasting days 
                fpdep=1, # Forcasting for forcasting precipitation depth
                dsli=2,  # Days since last irrigation event
                dsle=2,  # Days since last watering event
                fpact='cancel', # What to do if forcast sais rain
                ieff=100)

# ------------------------------------------------------------------------------------- #
# Main Simulation
# ------------------------------------------------------------------------------------- #

    #Run the model
    mdl = Model(planting_doy, harvest_doy, par, wth, 
                autoirr=airr, 
                ponded=True, 
                # puddled=True,
                # cons_p=True,
                aq_Ks=True, 
                comment = f'{year} DSR -- CSSRI, Karnal')

    mdl.run()

    model_output = pd.DataFrame(mdl.odata)
    output_file = os.path.join(base_dir, f'./DSR_{year}_daily_SWB_CSSRI.csv')
    file_exists = os.path.isfile(output_file)
    model_output.to_csv(output_file, mode='a', header=not file_exists, index=False)


    mdl.savesums(os.path.join(base_dir,f'DSR.{year}.CSSRI.sum'))
    mdl.savefile(os.path.join(base_dir,f'DSR.{year}.CSSRI.out'))


    # # Plot the model results
    required_columns = ['Day', 'Rain', 'Irrig', 'Runoff', 'DP', 'TAW', 'DAW', 'RAW', 'Dr', 'Ds', 'Vp']
    results_mdl = mdl.odata[required_columns]

    summary_data = mdl.swbdata
    summary_data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    summary_data['Year'] = year  # Add the year for reference
    summary_data['Planting_Date'] = planting_date
    if irrig != 0:
        irrig_crit_source = 'madDs'
    else:
        irrig_crit_source = 'mad'

    summary_data['Season'] = season
    summary_data['Irrig_Crit'] = irrig
    summary_data['Irrig_Crit_Source'] = irrig_crit_source

    # Reorder the dictionary to have specific keys first
    ordered_summary_data = {
        'timestamp': summary_data['timestamp'],
        'Year': summary_data['Year'],
        'Season': summary_data['Season'],
        'Planting_Date': summary_data['Planting_Date'],
        'Irrig_Crit_Source': summary_data['Irrig_Crit_Source'],  # Store the source of Irrig_Crit
        'Irrig_Crit': summary_data['Irrig_Crit']
    }

    # Add the rest of the original dictionary
    for key in summary_data:
        if key not in ordered_summary_data:
            ordered_summary_data[key] = round(summary_data[key], 3)

    return pd.DataFrame([ordered_summary_data])  # Convert to DataFrame for saving

    # df = mdl.odata
    # fig = go.Figure()
    # # Add traces (lines) for each of the variables: Kcadj, Ke, Kcb, Kcmax
    # fig.add_trace(go.Scatter(x=df['Day'], y=df['Kcadj'], mode='lines', name='Kcadj', line=dict(color='orange')))
    # fig.add_trace(go.Scatter(x=df['Day'], y=df['Ke'], mode='lines', name='Ke', line=dict(color='lightblue')))
    # fig.add_trace(go.Scatter(x=df['Day'], y=df['Kcb'], mode='lines', name='Kcb', line=dict(color='darkgreen')))
    # fig.add_trace(go.Scatter(x=df['Day'], y=df['Kcmax'], mode='lines', name='Kcmax', line=dict(color='gray')))

    # # Update layout to add labels and title
    # fig.update_layout(
    #     title="Time Series of Kcadj, Ke, Kcb, and Kcmax",
    #     xaxis_title="Day",
    #     yaxis_title="Coefficient Values",
    #     legend_title="Legend",
    #     xaxis=dict(
    #         tickmode='linear',  # Linear mode for custom ticks
    #         dtick=5             # Tick interval of 5 days
    #     ),
    #     legend=dict(x=0.5, xanchor='center', y=1.1, orientation='h'),  # Legend positioning
    #     template='plotly_white'  # Clean background
    # )
    # # plotly_fig.write_image(os.path.join(output_dir,f'DSR.{year}.CSSRI.jpg'))
    # fig.show()

    # # Show the plot
    # plotly_fig = WBPlot(results_mdl)
    # plotly_fig.show()

def run_simulations(base_dir, years_to_simulate, seasons, month_days, irrigation_levels):
    start_time = time.time()
    all_summary_data = []  # List to collect all DataFrames

    with ProcessPoolExecutor(max_workers=8) as executor:
        futures = []

        total_simulations = len(years_to_simulate) * len(seasons) * len(month_days) * len(irrigation_levels)
        current_simulation = 1       

        # Loop over the combinations of seasons, month_days, irrigation_crit, and years
        for year in years_to_simulate:
            for season in seasons:
                for month_day in month_days:
                    for irrigation_value in irrigation_levels:
                        futures.append(executor.submit(run, base_dir, year, season, month_day, irrigation_value))

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


def run_simulations(base_dir, years_to_simulate, seasons, month_days, irrigation_levels):
    start_time = time.time()
    all_summary_data = []  # List to collect all DataFrames

    # Using ProcessPoolExecutor for parallel execution
    with ProcessPoolExecutor(max_workers=8) as executor:  # You can adjust the number of workers
        futures = []

        total_simulations = len(years_to_simulate) * len(seasons) * len(month_days) * len(irrigation_levels)
        current_simulation = 0       

        # Loop over the combinations of seasons, month_days, irrigation_crit, and years
        for year in years_to_simulate:
            for season in seasons:
                for month_day in month_days:
                    for irrigation_level in irrigation_levels:
                        # Submit the task to the executor
                        mad = 0.06
                        futures.append(executor.submit(run, base_dir, year, season, month_day, irrigation_level))
                        

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

    # years_to_simulate = range(2017, 2020)  # Example years
    # seasons = [120, 135, 145]
    # month_days = ['05-15', '06-01', '06-15', '07-01', '07-15']
    # irrigation_levels = [0.47, 0.75, 0.94, 0]

    years_to_simulate = [2017]  # Example years
    seasons = [120]
    month_days = ['07-01']
    irrigation_levels = [0.75]


    # Run simulations and collect results
    final_df = run_simulations(base_dir, years_to_simulate, seasons, month_days, irrigation_levels)

    # Save the final DataFrame to CSV
    final_csv_path = os.path.join(base_dir, f'DSR_120-0.75-delayed_{datestamp}.csv')
    final_df.to_csv(final_csv_path, index=False)
    print(f"\nConsolidated summary saved to {final_csv_path}")


if __name__ == '__main__':
    main()


            
