from datetime import datetime, timedelta
import pandas as pd
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

def crop_parameters(crop_type):
    """
    Returns crop-specific parameters based on the crop type.
    """
    if crop_type == 'DSR':
        return Parameters(comment='DSR Rice for CSSRI Karnal, 2018',
                          Kcbini=0.15,
                          Kcbmid=1.15,
                          Kcbend=0.85,
                          Lini=30,
                          Ldev=45,
                          Lmid=25,
                          Lend=20,
                          hini=0.05,
                          hmax=1.1,
                          pbase=0.2,
                          Zrini=0.2,
                          Zrmax=0.6,
                          thetaFC=0.279509,
                          thetaWP=0.156771,
                          theta0=0.09707,
                          thetaS=0.36635,
                          # Ksat=49.0807,
                          Ksat=8.0807,
                          Bundh=0.3,
                          Ze=0.1,
                          REW=10,
                          CN2=70)

    elif crop_type == 'Potato':
        return Parameters(comment='Potato for CSSRI Karnal, 2018',
                          Kcbini=0.15,
                          Kcbmid=1.10,
                          Kcbend=0.10,
                          Lini=30,
                          Ldev=30,
                          Lmid=40,
                          Lend=30,
                          hini=0.05,
                          hmax=0.6,
                          pbase=0.4,
                          Zrini=0.1,
                          Zrmax=0.5,
                          thetaFC=0.279509,
                          thetaWP=0.156771,
                          theta0=0.09707,
                          thetaS=0.36635,
                          # Ksat=49.0807,
                          Ksat=8.0807,
                          Bundh=0.3,
                          Ze=0.1,
                          REW=10,
                          CN2=70)

    elif crop_type == 'Wheat':
        return Parameters(comment='Wheat for CSSRI Karnal, 2018',
                          Kcbini=0.15,
                          Kcbmid=1.10,
                          Kcbend=0.20,
                          Lini=30,
                          Ldev=30,
                          Lmid=40,
                          Lend=30,
                          hini=0.05,
                          hmax=1.1,
                          pbase=0.55,
                          Zrini=0.2,
                          Zrmax=1.2,
                          thetaFC=0.279509,
                          thetaWP=0.156771,
                          theta0=0.09707,
                          thetaS=0.36635,
                          # Ksat=49.0807,
                          Ksat=8.0807,
                          Bundh=0.3,
                          Ze=0.1,
                          REW=10,
                          CN2=70)

    elif crop_type == 'Maize':
        return Parameters(comment='Maize for CSSRI Karnal, 2018',
                          Kcbini=0.15,
                          Kcbmid=1.15,
                          Kcbend=0.25,
                          Lini=20,
                          Ldev=35,
                          Lmid=40,
                          Lend=30,
                          hini=0.1,
                          hmax=2.5,
                          pbase=0.5,
                          Zrini=0.2,
                          Zrmax=1.2,
                          thetaFC=0.279509,
                          thetaWP=0.156771,
                          theta0=0.09707,
                          thetaS=0.36635,
                          # Ksat=49.0807,
                          Ksat=8.0807,
                          Bundh=0.3,
                          Ze=0.1,
                          REW=10,
                          CN2=70)
    
    else:
        raise ValueError(f"Unsupported crop type: {crop_type}")

def run(crop_type, year, base_dir):
    # Get the relevant directory
    output_dir = os.path.join(base_dir, crop_type, str(year))
    os.makedirs(output_dir, exist_ok=True)

    # Get crop-specific parameters
    par = crop_parameters(crop_type)

    # Weather Data setup (same for all crops)
    wth = Weather(comment=f'{crop_type} CSSRI Karnal {year}\nSource: IMD & ISIMIP')
    wth.z = 252.64987
    wth.lat = 29.707983
    wth.wndht = 2
    weather_data = pd.read_csv("./data/CSSRI_daily_weather.csv")

    # Convert the 'date' column to datetime and extract year and day of year
    if 'DATE' in weather_data.columns:
        weather_data['DATE'] = pd.to_datetime(weather_data['DATE'], format='%Y-%m-%d')
        weather_data['YEAR'] = weather_data['DATE'].dt.year
        weather_data['DOY'] = weather_data['DATE'].dt.strftime('%j')

    # Create an empty DataFrame for weather data
    required_columns = ['Srad', 'Tmax', 'Tmin', 'Vapr', 'Tdew', 'RHmax', 'RHmin',
                        'Wndsp', 'Rain', 'ETref', 'MorP']
    wth.wdata = pd.DataFrame(columns=required_columns)

    column_mapping = { 'SRAD': 'Srad', 'TMAX': 'Tmax', 'TMIN': 'Tmin', 'VAPR': 'Vapr', 'TDEW': 'Tdew', 
                      'RHMAX': 'RHmax', 'RHMIN': 'RHmin', 'WNDSP': 'Wndsp', 'RAIN': 'Rain', 'ETREF': 'ETref', 
                      'MORP': 'MorP' }

    for csv_col, wdata_col in column_mapping.items():
        if csv_col in weather_data.columns:
            wth.wdata[wdata_col] = weather_data[csv_col]

    wth.wdata['MorP'] = 'M'
    wth.wdata.index = weather_data['YEAR'].astype(str) + '-' + weather_data['DOY']
    wth.savefile(os.path.join(output_dir, f'{crop_type}_CSSRI_IMD_daily_{year}.wth'))

    # Irrigation Data
    planting_date = f'{year}-05-15'  # Default for DSR, adjust per crop
    if crop_type == 'Wheat':
        planting_date = f'{year}-10-01'
    elif crop_type == 'Maize':
        planting_date = f'{year+1}-04-01'

    planting_datetime = datetime.strptime(planting_date, '%Y-%m-%d')
    total_growth_days = par.Lini + par.Ldev + par.Lmid + par.Lend
    harvest_datetime = planting_datetime + timedelta(days=total_growth_days)
    irrig_cutoff = harvest_datetime - timedelta(days=14)

    planting_doy = planting_datetime.strftime('%Y-%j')
    harvest_doy = harvest_datetime.strftime('%Y-%j')
    irrig_cutoff_doy = irrig_cutoff.strftime('%Y-%j')

    airr = AutoIrrigate()
    if crop_type == 'Rice':
        airr.addset(planting_doy, irrig_cutoff_doy, madDs=0.2, wdpth=0, fpday=1, fpdep=1, fpact='cancel', ieff=100)
    elif crop_type == 'Wheat':
        airr.addset(planting_doy, irrig_cutoff_doy, mad=0.75, wdpth=0, fpday=1, fpdep=1, fpact='cancel', ieff=100)
    elif crop_type == 'Maize':
        airr.addset(planting_doy, irrig_cutoff_doy, mad=0.75, wdpth=0, fpday=1, fpdep=1, fpact='cancel', ieff=100)

    # Run the Model
    mdl = Model(planting_doy, harvest_doy, par, wth, autoirr=airr, ponded=True, aq_Ks=True, comment=f'{year} {crop_type} CSSRI, Karnal')
    mdl.run()

    # Save results
    mdl.savesums(os.path.join(output_dir, f'{year}_{crop_type}_CSSRI.sum'))
    mdl.savefile(os.path.join(output_dir, f'{year}_{crop_type}_CSSRI.out'))

    # Plot the results
    required_columns = ['Day', 'Rain', 'Irrig', 'Runoff', 'DP', 'TAW', 'DAW', 'RAW', 'Dr', 'Ds', 'Vp']
    results_mdl = mdl.odata[required_columns]
    plotly_fig = WBPlot(results_mdl)
    plotly_fig.show()

    # Summary data
    summary_data = mdl.swbdata
    summary_data['Year'] = year
    summary_df = pd.DataFrame([summary_data])
    summary_csv_path = os.path.join(output_dir, f'{year}_{crop_type}_CSSRI_summary.csv')
    summary_df.to_csv(summary_csv_path, index=False)
    print(f'Summary data saved to {summary_csv_path}')

    return summary_csv_path

def main():
    base_dir = os.path.join(os.path.dirname(__file__), "results")
    # years_to_simulate = range(1989, 2020)
    years_to_simulate = range(2017, 2018)
    crops = ['DSR', 'Wheat', 'Maize']
    # crops = ['Wheat']

    all_summary_paths = []

    for crop in crops:
        for year in years_to_simulate:
            summary_path = run(crop, year, base_dir)
            all_summary_paths.append(summary_path)

    all_summaries = []
    for summary_path in all_summary_paths:
        summary_df = pd.read_csv(summary_path)
        all_summaries.append(summary_df)

    consolidated_summary = pd.concat(all_summaries, ignore_index=True)
    consolidated_summary_path = os.path.join(base_dir, "summary_all_years.csv")
    consolidated_summary.to_csv(consolidated_summary_path, index=False)
    print(f"Consolidated summary saved to {consolidated_summary_path}")

if __name__ == '__main__':
    main()
