import plotly.graph_objects as pl

def WBPlot(results):
    # Plot 2: Rainfall, Irrigation, TAW, RAW, Dr & DP
    fig = pl.Figure()

    fig.add_trace(pl.Bar(x=results['Day'], y=results['Rain'], name='Rainfall', 
                         marker_color='dodgerblue', opacity=0.6, offsetgroup=1))
    fig.add_trace(pl.Bar(x=results['Day'], y=results['Irrig'], name='Irrigation', 
                         marker_color='green', offsetgroup=1))
    fig.add_trace(pl.Bar(x=results['Day'], y=results['Runoff'], name='Runoff', 
                         marker_color='yellow', offsetgroup=1))
    fig.add_trace(pl.Bar(x=results['Day'], y=-results['DP'], name='Percolation', 
                         marker_color='orange', offsetgroup=1))

    fig.add_trace(pl.Scatter(x=results['Day'], y=-results['TAW'], mode='lines', 
                             line=dict(color='brown'), name='TAW'))
    fig.add_trace(pl.Scatter(x=results['Day'], y=-results['DAW'], mode='lines', 
                             line=dict(color='lightblue', width=2), name='DAW'))

    fig.add_trace(pl.Scatter(x=results['Day'], y=-results['RAW'], mode='lines', 
                             line=dict(color='darkslategrey', width=2), name='RAW'))

    fig.add_trace(pl.Scatter(x=results['Day'], y=-results['Dr'], mode='lines', 
                             line=dict(color='red', width=2), name='Dr'))
    fig.add_trace(pl.Scatter(x=results['Day'], y=-results['Ds'], mode='lines', 
                             line=dict(color='blue', width=2), name='Ds'))
    fig.add_trace(pl.Scatter(x=results['Day'], y=results['Vp'], mode='lines', 
                             line=dict(color='blue', width=2), name='Vp'))


    # Update axes
    fig.update_yaxes(
        title_text='[mm]',
        dtick=10,
        tickmode='linear',
        showgrid=True      # Enable grid lines for x-axis
    )
    fig.update_xaxes(
        title_text='Days after sowing',
        dtick=5,     # Weekly ticks (milliseconds in a week)
        tickmode='linear',
        showgrid=True      # Enable grid lines for x-axis
    )

    # Update layout
    fig.update_layout(
        barmode = 'relative',
        title="Water Balance Components",
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        template="plotly_white",
        showlegend=True
    )

    return fig
