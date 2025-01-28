import pandas as pd
import datetime
import math

class Landprep:

    def __init__(self, start, end, par, wth, ieff=0, comment=''):

        self.startDate = datetime.datetime.strptime(start, '%Y-%j')
        self.endDate   = datetime.datetime.strptime(end, '%Y-%j')
        self.par = par
        self.wth = wth
        self.ieff = ieff
        self.comment = 'Comments: ' + comment.strip()
        self.tmstmp = datetime.datetime.now()
        self.cnames = ['Date', 'Year', 'DOY', 'DOW', 'Day', 'ETref',
                'ETc', 'ETcadj', 'Kcmax', 'fw', 'E', 'K', 'Kr', 'De', 'DPe',
                'Irrig', 'IrrLoss', 'Rain', 'Runoff', 'DP', 'TAW', 'DAW',
                'Veff', 'Vp', 'Vs', 'Vr', 'Ds', 'Dr', 'fDr', 'fDs', 'theta0']

        self.odata = pd.DataFrame(columns=self.cnames)

    def __str__(self):

        self.tmstmp = datetime.datetime.now()
        timestamp = self.tmstmp.strftime('%Y-%m-%d %H:%M:%S')
        sdate = self.startDate.strftime('%Y-%m-%d')
        edate = self.endDate.strftime('%Y-%m-%d')

        solmthd = 'D - Default FAO-56 homogenous soil bucket approach'

        ast='*'*72

        keys = [ 'Year-DOY', 'Date', 'Year', 'DOY', 'DOW', 'Day', 'ETref',
                'ETc', 'ETcadj', 'Kcmax', 'fw', 'E', 'K', 'Kr', 'De', 'DPe',
                'Irrig', 'IrrLoss', 'Rain', 'Runoff', 'DP', 'TAW', 'DAW',
                'Veff', 'Vp', 'Vs', 'Vr', 'Ds', 'Dr', 'fDr', 'fDs', 'theta0']

        header = (
            f'{keys[0]:>8s}'  # Date
            f'{keys[1]:>12s}'   # DOY
            f'{keys[2]:>8s}'   # Day
            f'{keys[3]:>5s}'   # Day
            f'{keys[4]:>5s}'   # Day
            f'{keys[5]:>5s}'   # Day
            + ''.join(f'{key:>8s}' for key in keys[6:])
        )

        fmts = {
            # Temporal Data
            'Year-DOY': '{:8s}'.format,
            'Date': '{:12s}'.format,
            'Year': '{:3s}'.format,
            'DOY': '{:3s}'.format,
            'DOW': '{:3s}'.format,
            'Day': '{:3s}'.format,
            # Evapotranspiration
            'ETref': '{:7.3f}'.format,
            'ETc': '{:7.3f}'.format,
            'ETcadj': '{:7.3f}'.format,
            'E': '{:7.3f}'.format,
            # Crop parameters
            'K': '{:7.3f}'.format,
            'Kr': '{:7.3f}'.format,
            'Kcmax': '{:7.3f}'.format,
            # Evaporation
            'fw': '{:7.3f}'.format,
            'De': '{:7.3f}'.format,
            'DPe': '{:7.3f}'.format,
            # Surface components
            'Irrig': '{:7.3f}'.format,
            'IrrLoss': '{:7.3f}'.format,
            'Rain': '{:7.3f}'.format,
            'Runoff': '{:7.3f}'.format,
            # Soil Water Balance
            'DP': '{:7.3f}'.format,
            'TAW': '{:7.3f}'.format,
            'DAW': '{:7.3f}'.format,
            'Veff': '{:7.3f}'.format,
            'Vp': '{:7.3f}'.format,
            'Vs': '{:7.3f}'.format,
            'Vr': '{:7.3f}'.format,
            'Ds': '{:7.3f}'.format,
            'Dr': '{:7.3f}'.format,
            'fDr': '{:7.3f}'.format,
            'fDs': '{:7.3f}'.format,
            'theta0': '{:7.3f}'.format,
        }

        s = (
            f'{ast}\n'
            'pyfao56: FAO-56 Evapotranspiration in Python\n'
            'Output Data\n'
            f'Timestamp: {timestamp}\n'
            f'Simulation start date: {sdate}\n'
            f'Simulation end date: {edate}\n'
            f'Soil method: {solmthd}\n'
            f'{ast}\n'
            f'{self.comment}\n'
            f'{ast}\n'
            f'{header}\n'
        )

        if not self.odata.empty:
            s += self.odata.to_string(header=False, formatters=fmts)

        return s

    def savefile(self,filepath='pyfao56.out'):
        try:
            f = open(filepath, 'w')
        except FileNotFoundError:
            print('The filepath for output data is not found.')
        else:
            f.write(self.__str__())
            f.close()

    def savecsv(self, filepath='pyfao56_summary.csv'):
        keys = [
            'Date', 'DOY', 'Day', 'ETref', 'ETc', 'ETcadj', 'DP', 'Irrig',
            'IrrLoss', 'Rain', 'Runoff', 'TAW', 'DAW', 'Veff', 'Vp',
            'Vs', 'Vr', 'Ds', 'Dr', 'fDr'
        ]

        # Ensure the keys are in the odata columns
        valid_keys = [key for key in keys if key in self.odata.columns]
        
        if not valid_keys:
            print('No valid keys to save in summary. Please check odata.')
            return

        # Create a new DataFrame with the selected keys
        summary_df = self.odata[valid_keys]
        summary_df = summary_df.round(4)

        try:
            # Save to CSV
            summary_df.to_csv(filepath, index=False)
            print(f"Summary successfully saved to {filepath}")
        except FileNotFoundError:
            print('The filepath for the summary data is not found.')


    def savesums(self, filepath='pyfao56.sum'):
        self.tmstmp = datetime.datetime.now()
        timestamp = self.tmstmp.strftime('%Y-%m-%d %H:%M:%S')
        sdate = self.startDate.strftime('%Y-%m-%d')
        edate = self.endDate.strftime('%Y-%m-%d')

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
            ).format(ast,timestamp,sdate,edate,ast,self.comment,ast)
        if not self.odata.empty:
            keys = ['ETref','ETc','ETcadj','DP','Irrig',
                    'IrrLoss','Rain','Runoff','Veff_ini','Veff_end']
            for key in keys:
                s += '{:8.0f} : {:s}\n'.format(self.swbdata[key],key)

        try:
            f = open(filepath, 'w')
        except FileNotFoundError:
            print('The filepath for summary data is not found.')
        else:
            f.write(s)
            f.close()

#---------------------------------------------------------------------------
# Main calculations
#---------------------------------------------------------------------------

    class ModelState:

        pass

    def run(self):
        """Initialize model, conduct simulations, update self.odata"""

        tcurrent = self.startDate
        tdelta = datetime.timedelta(days=1)

        #Initialize model state
        io = self.ModelState()
        io.i = 0

        io.Lnrs = self.par.Lnrs
        io.Lprp = self.par.Lprp
        io.Wdpud = self.par.Wdpud
        io.Kcdry = self.par.Kcdry
        io.Kcwet = self.par.Kcwet
        io.Puddays = self.par.Puddays
        io.hini    = self.par.hini

        io.thetaFC = self.par.thetaFC
        io.thetaWP = self.par.thetaWP
        io.theta0  = self.par.theta0
        io.thetaS  = self.par.thetaS
        io.Ksat    = self.par.Ksat

        io.fw = 1.0
        io.h = io.hini
        io.wndht  = self.wth.wndht

        io.Zp = self.par.Zp
        io.Ze = self.par.Ze

        io.REW = self.par.REW
        io.Bundh = self.par.Bundh * 1000

        io.ieff = self.ieff

        io.lamb = 1 / io.Puddays * math.log(io.Ksat**0.33 / io.Ksat)

        io.DP = 0.0

        #Total evaporable water (TEW, mm) - FAO-56 Eq. 73
        io.TEW = 1000. * (io.thetaFC - 0.50 * io.thetaWP) * io.Ze
        #Initial root zone drainable available water (DAW, mm)
        io.DAW = 1000. * (io.thetaS - io.thetaFC) * io.Zp
        #Initial depth of evaporation (De, mm) - FAO-56 page 153
        io.De = 1000. * (io.thetaFC - 0.50 * io.thetaWP) * io.Ze
        #Initial root zone depletion (Dr, mm) - FAO-56 Eq. 87
        io.Dr = 1000. * (io.thetaFC - io.theta0) * io.Zp
        #Initial root zone residual available water (TAW, mm)
        io.TAW = 1000. * (io.thetaFC - io.thetaWP) * io.Zp
        #By default, FAO-56 doesn't consider the following variables


        #Initial effective available moisture (Vtot, mm)
        #NOTE: This accounts for all the water in the paddy and can exceed 
        #TAW + DAW, hence the different nomenclature to prevent confusion.
        io.Veff = 1000 * (io.theta0 - io.thetaWP) * io.Zp
        # Initial ponding depth (Vp, mm)
        io.Vp = sorted([0.0, io.Veff - io.DAW - io.TAW, io.Bundh])[1]
        # Initial saturation depth (Vs, mm)
        io.Vs = sorted([0.0, io.Veff - io.Vp - io.TAW, io.DAW])[1]
        # Initial residual soil moisture (Vr, mm)
        io.Vr = sorted([0.0, io.Veff - io.Vp - io.Vs, io.TAW])[1]

        io.Ds = sorted([0.0, io.DAW - io.Vp, io.Bundh])[1]

        io.DP = sorted([0.0, io.Vs + io.Vp, io.Ksat])[1]

        #Initial puddle depletion fraction (fDr, mm/mm)
        io.fDr = 1.0 - ((io.TAW - io.Dr) / io.TAW)

        self.odata = pd.DataFrame(columns=self.cnames)

        while tcurrent <= self.endDate:
            mykey = tcurrent.strftime('%Y-%j')

            #Update ModelState object
            io.ETref = self.wth.wdata.loc[mykey,'ETref']
            if math.isnan(io.ETref):
                io.ETref = self.wth.compute_etref(mykey)
            io.rain = self.wth.wdata.loc[mykey,'Rain']
            io.wndsp = self.wth.wdata.loc[mykey,'Wndsp']
            if math.isnan(io.wndsp):
                io.wndsp = 2.0
            io.rhmin = self.wth.wdata.loc[mykey,'RHmin']
            if math.isnan(io.rhmin):
                tmax = self.wth.wdata.loc[mykey,'Tmax']
                tmin = self.wth.wdata.loc[mykey,'Tmin']
                tdew = self.wth.wdata.loc[mykey,'Tdew']

            # Calculate RHmin from dewpoint temperature
                if math.isnan(tdew):
                    tdew = tmin
                #ASCE (2005) Eqs. 7 and 8
                emax = 0.6108*math.exp((17.27*tmax)/(tmax+237.3))
                ea   = 0.6108*math.exp((17.27*tdew)/(tdew+237.3))
                io.rhmin = ea/emax*100.
            if math.isnan(io.rhmin):
                io.rhmin = 45.

            io.idep = 0.0
            io.ieff = 100.0

            if io.i < io.Lprp - io.Puddays:
                io.idep = io.Ds + io.Dr
            elif io.Vp < io.Wdpud:
                io.idep = io.Ds + io.Dr + io.Wdpud

            #Advance timestep
            self._advance(io)

            #Append results to self.odata
            year = tcurrent.strftime('%Y')
            doy = tcurrent.strftime('%j') #Day of Year
            dow = tcurrent.strftime('%a') #Day of Week
            dat = tcurrent.strftime('%Y-%m-%d') #Date yyyy-mm-dd

            data = [ dat, year, doy, dow, str(io.i), io.ETref, io.ETc,
                    io.ETcadj, io.Kcmax, io.fw, io.E, io.K, io.Kr, io.De, io.DPe,
                    io.idep, io.irrloss, io.rain, io.runoff, io.DP, io.TAW,
                    io.DAW, io.Veff, io.Vp, io.Vs, io.Vr, io.Ds, io.Dr,
                    io.fDr, io.fDs, io.theta0 ]

            self.odata.loc[mykey] = data

            tcurrent = tcurrent + tdelta
            io.i+=1

        sdoy = self.startDate.strftime("%Y-%j")
        edoy = self.endDate.strftime("%Y-%j")

        self.swbdata = {
            'ETref': sum(self.odata['ETref']),
            'ETc': sum(self.odata['ETc']),
            'ETcadj': sum(self.odata['ETcadj']),
            'E': sum(self.odata['E']),
            'T': 0,
            'DP': sum(self.odata['DP']),
            'K': self.odata['K'].mean(),  # Mean of Hydraulic konductivity
            'Rain': sum(self.odata['Rain']),
            'Runoff': sum(self.odata['Runoff']),
            'Irrig': sum(self.odata['Irrig']),
            'IrrLoss': sum(self.odata['IrrLoss']),
            'Gross_Irrig': sum(self.odata['Irrig'] + self.odata['IrrLoss']),
            'Num_Irrig': len(self.odata[self.odata['Irrig'] > 0]),  # Count of non-zero irrigation values
            'Mean_Irrig': self.odata[self.odata['Irrig'] > 0]['Irrig'].mean(),  # Mean of non-zero irrigation values
            'Dr_ini': self.odata.loc[sdoy, 'Dr'],
            'Dr_end': self.odata.loc[edoy, 'Dr'],
            'Veff_ini': self.odata.loc[sdoy, 'Veff'],
            'Veff_end': self.odata.loc[edoy, 'Veff'],
            # New additions
        }

    def _advance(self, io):
        """Advance the model by one daily timestep. """

        #Losses due to irrigation inefficiency (irrloss, mm)
        io.irrloss = io.idep * (1 - io.ieff / 100.)

        #Effective irrigation (mm)
        effirr = max(0, io.idep - io.irrloss)

        io.runoff = 0 # NOTE: Placeholder

        #Effective precipitation (mm)
        effrain = max(0, io.rain - io.runoff)
        
        io.K = sorted([io.Ksat**0.33, 
                        io.Ksat * math.exp(io.lamb * (io.i + 1 - io.Lprp + io.Puddays)), 
                        io.Ksat])[1]


        #Upper limit crop coefficient (Kcmax) - FAO-56 Eq. 72
        u2 = io.wndsp * (4.87/math.log(67.8*io.wndht-5.42))
        u2 = sorted([1.0,u2,6.0])[1]
        rhmin = sorted([20.0,io.rhmin,80.0])[1]

        io.Kcmax = 1.2+(0.04*(u2-2.0)-0.004*(rhmin-45.0))* (io.h/3.0)**.3

        if io.Dr == 0:
            io.Kr = 1.0
        else:
            #Evaporation reduction coefficient (Kr, 0-1) - FAO-56 Eq. 74
            io.Kr = sorted([0.0,(io.TEW-io.De)/(io.TEW-io.REW),1.0])[1]

        #Soil water evaporation (E, mm) - FAO-56 Eq. 69
        io.E = io.Kcmax * io.ETref

        io.ETc = io.E 
        io.ETcadj = io.E

        # NOTE: DPe is used for De and De is used for Kr further up. They
        # reference eachother!

        #Deep percolation under exposed soil (DPe, mm) - FAO-56 Eq. 79
        DPe = effrain + effirr/io.fw - io.De
        io.DPe = sorted([0.0, DPe, io.K])[1]

        #Cumulative depth of evaporation (De, mm) - FAO-56 Eqs. 77 & 78
        De = io.De - effrain - effirr/io.fw + io.E/io.fw + io.DPe
        io.De = sorted([0.0,De,io.TEW])[1]

        Veff = io.Veff + effrain + effirr - io.E - io.DP
        io.Veff = max([Veff, 0.0])

        # Ponding depth (Vp, mm)
        io.Vp = sorted([0.0, io.Veff - io.DAW - io.TAW, io.Bundh])[1]
        # Saturation depth (Vs, mm)
        io.Vs = sorted([0.0, io.Veff - io.Vp - io.TAW, io.DAW])[1]
        # Residual soil moisture (Vr, mm)
        io.Vr = sorted([0.0, io.Veff - io.Vp - io.Vs, io.TAW])[1]

        # Deep percolation: If drainable water available
        io.DP = sorted([0.0, io.Vs, io.K])[1]

        #Root zone saturated soil water depletion (Ds,mm)
        io.Ds = max(0.0, io.DAW - io.Vs)
        #Root zone residual soil water depletion (Dr,mm)
        io.Dr = max(0.0, io.TAW - io.Vr)

        #Root zone soil water depletion fraction (fDr, mm/mm)
        io.fDr = 1.0 - ((io.TAW - io.Dr) / io.TAW)

        #Saturation zone soil water depletion fraction (fDr, mm/mm)
        io.fDs = 1.0 - ((io.DAW - io.Ds) / io.DAW)

        io.theta0 = io.Veff / (1000 * io.Zp) + io.thetaWP
