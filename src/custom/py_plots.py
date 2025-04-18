import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def WBPlot(results, crop_type, year, planting_date, irrigation_method, irrigation_level):
    # Ensure 'Day' is numeric for plotting
    results['Day'] = pd.to_numeric(results['Day'], errors='coerce')
    
    # Create figure and axis
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Bar plot for Rain, Irrigation, Runoff, and Percolation
    ax1.bar(results['Day'], results['Rain'], label='Rainfall', color='dodgerblue', alpha=0.6, width=1, align='center')
    ax1.bar(results['Day'], results['Irrig'], label='Irrigation', color='green', width=1, align='center')
    ax1.bar(results['Day'], results['Runoff'], label='Runoff', color='yellow', width=1, align='center')
    ax1.bar(results['Day'], -results['DP'], label='Percolation', color='orange', width=1, align='center')

    # Line plots for TAW, DAW, RAW, Dr, Ds, and Vp
    ax1.plot(results['Day'], -results['TAW'], color='brown', label='TAW', linewidth=2)
    ax1.plot(results['Day'], -results['DAW'], color='lightblue', label='DAW', linewidth=2)
    ax1.plot(results['Day'], -results['RAW'], color='darkslategrey', label='RAW', linewidth=2)
    ax1.plot(results['Day'], -results['Dr'], color='red', label='Dr', linewidth=2)
    ax1.plot(results['Day'], -results['Ds'], color='blue', label='Ds', linewidth=2)
    ax1.plot(results['Day'], results['Vp'], color='blue', label='Vp', linewidth=2)

    # Labels for y-axis
    ax1.set_ylabel('[mm]')

    # Ticks and grid for y-axis and x-axis
    ax1.tick_params(axis='y', direction='in', length=6)
    ax1.grid(True, axis='x', linestyle='--', alpha=0.5)
    ax1.set_xticks(np.arange(0, max(results['Day']) + 1, 5))  # Weekly ticks (assuming Day is in days)

    # Labels and title
    ax1.set_xlabel('Days after sowing')
    fig.suptitle(f"Water Balance Components for {crop_type}; {planting_date}; {irrigation_method}; {irrigation_level}")

    # Legend
    ax1.legend(loc='center', bbox_to_anchor=(0.5, -0.2), ncol=3)

    # Set figure size in pixels
    dpi = 100
    width_in_inches = 1500 / dpi  # 1500 pixels at 100 dpi
    height_in_inches = 600 / dpi  # 600 pixels at 100 dpi

    # Create the plot with the desired size
    fig.set_size_inches(width_in_inches, height_in_inches)

    return fig
