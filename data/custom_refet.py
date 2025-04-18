import math
import datetime
import pandas as pd

def ascedaily(rfcrp,z,lat,doy,israd,tmax,tmin,
              vapr=float('NaN'),tdew=float('NaN'),
              rhmax=float('NaN'),rhmin=float('NaN'),
              wndsp=float('NaN'),wndht=2.0):

    #tavg (float) : Mean daily air temperature (deg C)
    #ASCE (2005) Eq. 2
    tavg = (tmax+tmin)/2.0

    #patm (float) : Mean atmospheric pressure at weather station (kPa)
    #ASCE (2005) Eq. 3
    patm = 101.3*((293.0-0.0065*z)/293.0)**5.26

    #psycon (float) : Psychrometric constant (kPa (deg C)^-1)
    #ASCE (2005) Eq. 4
    psycon = 0.000665*patm

    #Udelta (float) : Slope of the saturation vapor pressure
    #temperature curve (kPa (deg C)^-1)
    #ASCE (2005) Eq. 5
    Udelta = 2503.0*math.exp(17.27*tavg/(tavg+237.3))
    Udelta = Udelta/((tavg+237.3)**2.0)

    #es (float) : Saturation vapor pressure (kPa)
    #ASCE (2005) Eqs. 6 and 7
    emax = 0.6108*math.exp((17.27*tmax)/(tmax+237.3))
    emin = 0.6108*math.exp((17.27*tmin)/(tmin+237.3))
    es = (emax+emin)/2.0

    #ea (float): Actual vapor pressure (kPa) ASCE (2005) Table 3
    if not math.isnan(vapr):
        #ASCE (2005) Table 3
        ea = vapr
    elif not math.isnan(tdew):
        #ASCE (2005) Eq. 8
        ea = 0.6108*math.exp((17.27*tdew)/(tdew+237.3))
    elif not math.isnan(rhmax) and not math.isnan(rhmin):
        #ASCE (2005) Eq. 11
        ea = (emin*rhmax/100. + emax*rhmin/100.)/2.0
    elif not math.isnan(rhmax):
        #ASCE (2005) Eq. 12
        ea = emin*rhmax/100.
    elif not math.isnan(rhmin):
        #ASCE (2005) Eq. 13
        ea = emax*rhmin/100.
    else:
        #ASCE (2005) Appendix E
        tdew = tmin - 2.0
        ea = 0.6108*math.exp((17.27*tdew)/(tdew+237.3))

    #rns (float) : Net shortwave radiation (MJ m^-2 d^-1)
    #ASCE (2005) Eq. 16
    albedo = 0.23
    rns = (1.0-albedo)*israd

    #ra (float) : Extraterrestrial radiation (MJ m^-2 d^-1)
    #ASCE (2005) Eqs. 21-27
    latrad = lat*math.pi/180.0 #Eq. 22
    dr = 1.0+0.033*math.cos(2.0*math.pi/365.0*doy) #Eq. 23
    ldelta = 0.409*math.sin(2.0*math.pi/365.0*doy-1.39) #Eq. 24
    ws = math.acos(-1.0*math.tan(latrad)*math.tan(ldelta)) #Eq. 27
    ra1 = ws*math.sin(latrad)*math.sin(ldelta) #Eq. 21
    ra2 = math.cos(latrad)*math.cos(ldelta)*math.sin(ws) #Eq. 21
    ra = 24.0/math.pi*4.92*dr*(ra1+ra2) #Eq. 21

    #rso (float) : Clear sky solar radiation (MJ m^-2 d^-1)
    #ASCE (2005) Eq. 19
    rso = (0.75+2e-5*z)*ra

    #rnl (float) : Net longwave radiation (MJ m^-2 d^-1)
    #ASCE (2005) Eqs. 17 and 18
    ratio = sorted([0.3,israd/rso,1.0])[1]
    fcd = sorted([0.05,1.35*ratio-0.35,1.0])[1] #Eq. 18
    tk4 = ((tmax+273.16)**4.0+(tmin+273.16)**4.0)/2.0 #Eq. 17
    rnl = 4.901e-9*fcd*(0.34-0.14*math.sqrt(ea))*tk4 #Eq. 17

    #rn (float) : Net radiation (MJ m^-2 d^-1)
    #ASCE (2005) Eq. 15
    rn = rns-rnl

    #g (float) : Soil heat flux (MJ m^-2 d^-1)
    #ASCE (2005) Eq. 30
    g = 0.0

    #u2 (float) : Wind profile relationship (m s^-1)
    #ASCE (2005) Eq. 33 and Appendix E
    if math.isnan(wndsp): wndsp = 2.0
    u2 = wndsp * (4.87/math.log(67.8*wndht-5.42))

    #Aerodynamic roughness and surface resistance constants
    #ASCE (2005) Table 1
    if rfcrp == 'S': #Short reference crop (0.12-m grass)
        Cn = 900.0  #K mm s^3 Mg^-1 d^-1
        Cd = 0.34   #s m^-1
    elif rfcrp == 'T': #Tall reference crop (0.50-m alfalfa)
        Cn = 1600.0 #K mm s^3 Mg^-1 d^-1
        Cd = 0.38   #s m^-1

    #etsz (float) : Standardized daily reference crop ET (mm d^-1)
    #ASCE (2005) Eq. 1
    etsz = 0.408*Udelta*(rn-g)+psycon*(Cn/(tavg+273.0))*u2*(es-ea)
    etsz = etsz/(Udelta+psycon*(1.0+Cd*u2))

    return etsz

def main():
    # Path to the input CSV file
    input_file = './CSSRI_daily_weather.csv'
    
    # Path to the output CSV file where ET0 will be appended
    output_file = './CSSRI_daily_weather_ET0.csv'
    # Read in the data from the input CSV file
    df = pd.read_csv(input_file)
    
    # Create a new column 'ET0' to store the calculated ET0 values
    et0_values = []
    
    # Loop through each row of the DataFrame and calculate ET0
    for index, row in df.iterrows():
        # Extract necessary values from the row
        rfcrp = 'S' 
        z = 252.64987
        lat = 29.707983
        # Convert the 'DATE' string to a datetime object and extract DOY
        date_str = row['DATE']
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        doy = date_obj.timetuple().tm_yday  # Day of Year
        israd = row['SRAD']
        tmax = row['TMAX']
        tmin = row['TMIN']
        vapr = row.get('VAPR', float('NaN'))
        tdew = row.get('TDEW', float('NaN'))
        rhmax = row.get('RHMAX', float('NaN'))
        rhmin = row.get('RHMIN', float('NaN'))
        wndsp = row.get('WNDSP', float('NaN'))
        wndht = 2.0
        
        # Call the ascedaily function to calculate ET0 for each row
        et0 = ascedaily(rfcrp, z, lat, doy, israd, tmax, tmin, 
                        vapr=vapr, tdew=tdew, rhmax=rhmax, rhmin=rhmin, 
                        wndsp=wndsp, wndht=wndht)
        
        # Append the calculated ET0 value to the list
        et0_values.append(et0)
    
    # Add the ET0 values to the DataFrame
    df['ET0'] = et0_values
    
    # Append the DataFrame with ET0 to the output CSV file (no header if the file exists)
    df.to_csv(output_file, index=False, mode='a', header=not pd.io.common.file_exists(output_file))
    
    print(f"ET0 values have been appended to {output_file}")

# Example usage of the main function
if __name__ == "__main__":
    main()

