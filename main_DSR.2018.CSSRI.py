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

def run(year, base_dir):

    output_dir = os.path.join(base_dir, str(year))
    os.makedirs(output_dir, exist_ok=True)

    # Specify the model parameters
    par = Parameters(comment = 'DSR Rice for CSSRI Karnal')

    par.Kcbini = 0.15
    par.Kcbmid = 1.00
    par.Kcbend = 0.75
    par.Lini = 30
    par.Ldev = 45
    par.Lmid = 25
    par.Lend = 20
    par.hini = 0.05
    par.hmax = 1.1
    par.thetaFC = 0.279509
    par.thetaWP = 0.156771
    par.theta0 = 0.09707
    par.thetaS = 0.36635
    par.Ksat = 49.0807
    par.Zrini = 0.2
    par.Zrmax = 0.6
    par.Bundh = 0.3
    par.pbase = 0.2
    par.Ze = 0.1
    par.REW =10
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
    weather_data = pd.read_csv("./data/CSSRI_daily_weather.csv")

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

    column_mapping = { 'SRAD': 'Srad', 'TMAX': 'Tmax', 'TMIN': 'Tmin', 'VAPR':
                      'Vapr', 'TDEW': 'Tdew', 'RHMAX': 'RHmax', 'RHMIN':
                      'RHmin', 'WNDSP': 'Wndsp', 'RAIN': 'Rain', 'ETREF':
                      'ETref', 'MORP': 'MorP' }

    for csv_col, wdata_col in column_mapping.items():
        if csv_col in weather_data.columns:
            wth.wdata[wdata_col] = weather_data[csv_col]

    wth.wdata['MorP'] = 'M'
    wth.wdata.index = weather_data['YEAR'].astype(str) + '-' + weather_data['DOY']

# ------------------------------------------------------------------------------------- #
# Irrigation Data
# ------------------------------------------------------------------------------------- #
    # Specify the planting date
    planting_date = f'{year}-06-01'

    # Convert planting date to a datetime object
    planting_datetime = datetime.strptime(planting_date, '%Y-%m-%d')
    total_growth_days = par.Lini + par.Ldev + par.Lmid + par.Lend
    harvest_datetime = planting_datetime + timedelta(days=total_growth_days)
    irrig_cutoff = harvest_datetime - timedelta(days=14)

    # Convert planting and harvest dates to YYYY-DOY format
    planting_doy = planting_datetime.strftime('%Y-%j')
    harvest_doy = harvest_datetime.strftime('%Y-%j')
    irrig_cutoff_doy = irrig_cutoff.strftime('%Y-%j')

    airr = AutoIrrigate()
    airr.addset(planting_doy, irrig_cutoff_doy,
                # for a derivation of these fractions see my 00_soil_data.ods file
                madDs=0.43,      # irrigate at 10 kPa (float, frac)
                # madDs=0.74,      # irrigate at 20 kPa (float, frac)
                # madDs=0.95,      # irrigate at 30 kPa (float, frac)
                # mad=0.07,      # irrigate at 40 kPa (float, frac)
                wdpth=0,    #[mm]
                fpday=1, # Forcasting days 
                fpdep=1, # Forcasting for forcasting precipitation depth
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

    mdl.savesums(os.path.join(output_dir,f'DSR.{year}.CSSRI.sum'))
    mdl.savefile(os.path.join(output_dir,f'DSR.{year}.CSSRI.out'))

    # # Plot the model results
    required_columns = ['Day', 'Rain', 'Irrig', 'Runoff', 'DP', 'TAW', 'DAW', 'RAW', 'Dr', 'Ds', 'Vp']
    results_mdl = mdl.odata[required_columns]

    plotly_fig = WBPlot(results_mdl)
    plotly_fig.show()
    # plotly_fig.write_image(os.path.join(output_dir,f'DSR.{year}.CSSRI.jpg'))

    summary_data = mdl.swbdata
    summary_data['Year'] = year  # Add the year for reference
    summary_df = pd.DataFrame([summary_data])  # Convert to DataFrame for saving
    summary_csv_path = os.path.join(output_dir, f'DSR.{year}.CSSRI_summary.csv')
    summary_df.to_csv(summary_csv_path, index=False)
    print(f'Summary data saved to {summary_csv_path}')

    # write df to csv 
    mdl.odata.to_csv(os.path.join(output_dir,f'DSR_{year}_CSSRI.csv'), index=False)

    df = mdl.odata
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

    # Show the plot
    fig.show()

    return summary_csv_path  # Return the path of the summary CSV

def main():
    # Base output directory
    today = datetime.now().strftime("%Y%m%d")
    base_dir = os.path.join(os.path.dirname(__file__), f"results_{today}")

    # Define the range of years to simulate
    years_to_simulate = range(1989, 2020)

    # List to store paths to all summary files
    all_summary_paths = []

    for year in years_to_simulate:
        summary_path = run(year, base_dir)
        all_summary_paths.append(summary_path)

    # Consolidate all summaries into a single CSV
    all_summaries = []

    for summary_path in all_summary_paths:
        summary_df = pd.read_csv(summary_path)
        all_summaries.append(summary_df)

    # Combine all summaries into a single DataFrame
    consolidated_summary = pd.concat(all_summaries, ignore_index=True)

    # Save the consolidated summary to a CSV
    consolidated_summary_path = os.path.join(base_dir, "summary_all_years.csv")
    consolidated_summary.to_csv(consolidated_summary_path, index=False)

    print(f"Consolidated summary saved to {consolidated_summary_path}")


if __name__ == '__main__':
    # This can be turned into a for loop to iterate over multiple years
    run(2018, os.path.join(os.path.dirname(__file__), "results"))
    # main()
