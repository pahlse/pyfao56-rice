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
        self.cnames = ['Date','Year','DOY','DOW','Day','ETref',
                       'ETc','ETcadj','T','E','p','Ks','h','Zr', 
                       'fc','tKcb','Kcb','Kcmax','Kc','Kcadj','Ke','Kr','fw',
                       'few','De','DPe','Irrig','IrrLoss','Rain',
                       'Runoff','DP','TAW','DAW','RAW','Veff','Vp',
                       'Vs','Vr','Ds','Dr','fDr', 'fDs', 'theta0','Se','K']

        self.odata = pd.DataFrame(columns=self.cnames)

    def __str__(self):

        self.tmstmp = datetime.datetime.now()
        timestamp = self.tmstmp.strftime('%Y-%m-%d %H:%M:%S')
        sdate = self.startDate.strftime('%Y-%m-%d')
        edate = self.endDate.strftime('%Y-%m-%d')

        solmthd = 'D - Default FAO-56 homogenous soil bucket approach'

        ast='*'*72

        keys = ['Year-DOY','Date','Year','DOY','DOW','Day','ETref',
                'ETc','ETcadj','T','E','p','Ks','h','Zr',
                'fc','tKcb','Kcb','Kcmax','Kc','Kcadj','Ke','Kr','fw',
                'few','De','DPe','Irrig','IrrLoss','Rain',
                'Runoff','DP','TAW','DAW','RAW','Veff','Vp',
                'Vs','Vr','Ds','Dr','fDr', 'fDs', 'theta0','Se','K']

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
            'T': '{:7.3f}'.format,
            'E': '{:7.3f}'.format,
            # Crop parameters
            'p': '{:7.3f}'.format,
            'Ks': '{:7.3f}'.format,
            'h': '{:7.3f}'.format,
            'Zr': '{:7.3f}'.format,
            'fc': '{:7.3f}'.format,
            # Kc-values
            'tKcb': '{:7.3f}'.format,
            'Kcb': '{:7.3f}'.format,
            'Kcmax': '{:7.3f}'.format,
            'Kc': '{:7.3f}'.format,
            'Kcadj': '{:7.3f}'.format,
            'Ke': '{:7.3f}'.format,
            'Kr': '{:7.3f}'.format,
            # Evaporation
            'fw': '{:7.3f}'.format,
            'few': '{:7.3f}'.format,
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
            'RAW': '{:7.3f}'.format,
            'Veff': '{:7.3f}'.format,
            'Vp': '{:7.3f}'.format,
            'Vs': '{:7.3f}'.format,
            'Vr': '{:7.3f}'.format,
            'Ds': '{:7.3f}'.format,
            'Dr': '{:7.3f}'.format,
            'fDr': '{:7.3f}'.format,
            'fDs': '{:7.3f}'.format,
            'theta0': '{:7.3f}'.format,
            'Se': '{:7.3f}'.format,
            'K': '{:7.3f}'.format,
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
            keys = [ 'ETref', 'ETc', 'ETcadj', 'E', 'T', 'DP', 'K', 'Rain',
                    'Runoff', 'Irrig', 'IrrLoss', 'Gross_Irrig', 'Num_Irrig',
                    'Mean_Irrig', 'Veff_ini', 'Veff_end' ]
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
        io.thetaR  = self.par.thetaR
        io.Ksat    = self.par.Ksat

        io.fw = 1.0
        io.Kcb = 0.0 # NOTE: See page 207 of FAO-56 (Bare soil case)
        io.fc = 0.0 # NOTE: See page 207 of FAO-56 (Bare soil case)
        io.Ks = 0.0 # NOTE: No crop growth so no stress
        io.h = 0.0 # NOTE: No crop growth -> Kcmax = 1.2

        io.wndht  = self.wth.wndht

        io.Zp = self.par.Zp
        io.Ze = self.par.Ze

        io.REW = self.par.REW
        io.Bundh = self.par.Bundh * 1000

        io.ieff = self.ieff

        io.p = -99.999
        io.Zr = -99.999
        io.tKcb = -99.999
        io.RAW = 0.0

        io.lamb = 1 / io.Puddays * math.log(io.Ksat**0.33 / io.Ksat)

        io.l = 0.50
        io.n = 1.3055
        io.m = 1 - 1/io.n

        # Initial K set by traditional van Genuchten method
        io.Se = sorted([0, (io.theta0 - io.thetaR)/ (io.thetaS - io.thetaR), 1])[1]
        Kini = sorted([0, io.Ksat * io.Se**0.5 * (1 - (1 - io.Se**(1/io.m))**io.m)**2, io.Ksat])[1]

        #Total evaporable water (TEW, mm) - FAO-56 Eq. 73
        io.TEW = 1000. * (io.thetaFC - 0.50 * io.thetaWP) * io.Ze
        #Initial depth of evaporation (De, mm) - FAO-56 page 153
        io.De = 1000. * (io.thetaFC - 0.50 * io.thetaWP) * io.Ze
        #Initial root zone drainable available water (DAW, mm)
        io.DAW = 1000. * (io.thetaS - io.thetaFC) * io.Zp
        #Initial root zone residual available water (TAW, mm)
        io.TAW = 1000. * (io.thetaFC - io.thetaWP) * io.Zp

        #Initial effective available moisture (Veff, mm)
        #NOTE: This accounts for all the water in the paddy and can exceed 
        #TAW + DAW, hence the different nomenclature to prevent confusion. 
        # Also, note that theta0 cannot exceed thetaWP.
        io.Veff = 1000 * (io.theta0 - io.thetaWP) * io.Zp
        # Initial ponding depth (Vp, mm)
        io.Vp = sorted([0.0, io.Veff - io.DAW - io.TAW, io.Bundh])[1]
        # Initial saturation depth (Vs, mm)
        io.Vs = sorted([0.0, io.Veff - io.Vp - io.TAW, io.DAW])[1]
        # Initial residual soil moisture (Vr, mm)
        io.Vr = sorted([0.0, io.Veff - io.Vp - io.Vs, io.TAW])[1]

        #Initial depletion of saturation (Ds, mm)
        io.Ds = sorted([0.0, io.DAW - io.Vs, io.DAW])[1]
        #Initial root zone depletion (Dr, mm) - FAO-56 Eq. 87
        io.Dr = sorted([0.0, io.TAW - io.Vr, io.TAW])[1]

        io.DP = sorted([0.0, io.Vs + io.Vp, Kini])[1]

        #Initial puddle depletion fraction (fDr, mm/mm)
        io.fDr = 1.0 - ((io.TAW - io.Dr) / io.TAW)
        io.fDs = 1.0 - ((io.DAW - io.Dr) / io.DAW)

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
            # During puddling irrigate when WD 0, refill to desired level defined in Wdpud
            elif io.Vp == 0: 
                io.idep = io.Ds + io.Dr + io.Wdpud

            #Advance timestep
            self._advance(io)

            #Append results to self.odata
            year = tcurrent.strftime('%Y')
            doy = tcurrent.strftime('%j') #Day of Year
            dow = tcurrent.strftime('%a') #Day of Week
            dat = tcurrent.strftime('%Y-%m-%d') #Date yyyy-mm-dd

            data = [
                dat, year, doy, dow, str(io.i),
                io.ETref, io.ETc, io.ETcadj, io.T, io.E,
                io.p, io.Ks, io.h, io.Zr, io.fc,
                io.tKcb, io.Kcb, io.Kcmax, io.Kc, io.Kcadj, io.Ke, io.Kr,
                io.fw, io.few, io.De, io.DPe,
                io.idep, io.irrloss, io.rain, io.runoff,
                io.DP, io.TAW, io.DAW, io.RAW, io.Veff, io.Vp, io.Vs, io.Vr,
                io.Ds, io.Dr, io.fDr, io.fDs, io.theta0, io.Se, io.K
            ]
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
            'T': sum(self.odata['T']),
            'DP': sum(self.odata['DP']),
            'K': self.odata['K'].mean(),  # Mean of Hydraulic konductivity
            'Rain': sum(self.odata['Rain']),
            'Runoff': sum(self.odata['Runoff']),
            'Irrig': sum(self.odata['Irrig']),
            'IrrLoss': sum(self.odata['Irrig'] *  (100 - io.ieff)/100),
            # 'Gross_Irrig': sum(self.odata['Irrig'] + self.odata['Irrig'] * (100 - io.ieff)/100),
            'Gross_Irrig': sum(self.odata['Irrig'] + self.odata['Irrig'] * 0.3),
            'Num_Irrig': len(self.odata[self.odata['Irrig'] > 0]),  # Count of non-zero irrigation values
            'Mean_Irrig': self.odata[self.odata['Irrig'] > 0]['Irrig'].mean(),  # Mean of non-zero irrigation values
            'Veff_ini': 1000 * (self.par.theta0 - io.thetaWP) * io.Zp,
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
        
        # K (mm/day); based on Gerardos code
        io.K = sorted([io.Ksat**0.33,  # this needs to be confirmed with literature
                        io.Ksat * math.exp(io.lamb * (io.i + 1 - io.Lprp + io.Puddays)), 
                        io.Ksat])[1]


        #Upper limit crop coefficient (Kcmax) - FAO-56 Eq. 72
        u2 = io.wndsp * (4.87/math.log(67.8*io.wndht-5.42))
        u2 = sorted([1.0,u2,6.0])[1]
        rhmin = sorted([20.0,io.rhmin,80.0])[1]

        io.Kcmax = 1.2+(0.04*(u2-2.0)-0.004*(rhmin-45.0)) * (io.h/3.0)**.3
        #Exposed & wetted soil fraction (few, 0.01-1.0) - FAO-56 Eq. 75
        io.few = sorted([0.01,min([1.0-io.fc, io.fw]),1.0])[1]

        #Evaporation reduction coefficient (Kr, 0-1) - FAO-56 Eq. 74
        # NOTE: The assumption is that soil stays wetted throughout the puddling process
        io.Kr = 1.0 
        if io.Dr > 0:
            io.Kr = sorted([0.0,(io.TEW-io.De)/(io.TEW-io.REW),1.0])[1]

        io.Ke = min([io.Kr*(io.Kcmax-io.Kcb), io.few*io.Kcmax])

        #Soil water evaporation (E, mm) - FAO-56 Eq. 69
        io.E = io.Ke * io.ETref

        #Deep percolation under exposed soil (DPe, mm) - FAO-56 Eq. 79
        DPe = effrain + effirr/io.fw - io.De
        io.DPe = sorted([0.0, DPe, io.K])[1]

        #Cumulative depth of evaporation (De, mm) - FAO-56 Eqs. 77 & 78
        De = io.De - effrain - effirr/io.fw + io.E/io.fw + io.DPe
        io.De = sorted([0.0,De,io.TEW])[1]

        #Crop coefficient (Kc) - FAO-56 Eq. 69
        io.Kc = io.Ke + io.Kcb

        #Non-stressed crop evapotranspiration (ETc, mm) - FAO-56 Eq. 69
        io.ETc = io.Kc * io.ETref

        #Adjusted crop coefficient (Kcadj) - FAO-56 Eq. 80
        io.Kcadj = io.Ks * io.Kcb + io.Ke

        #Adjusted crop evapotranspiration (ETcadj, mm) - FAO-56 Eq. 80
        io.ETcadj = io.Kcadj * io.ETref

        #Adjusted crop transpiration (T, mm)
        io.T = (io.Ks * io.Kcb) * io.ETref


        Veff = io.Veff + effrain + effirr - io.E - io.DP
        io.Veff = max([Veff, 0.0])

        # Ponding depth (Vp, mm)
        io.Vp = sorted([0.0, io.Veff - io.DAW - io.TAW, io.Bundh])[1]
        # Saturation depth (Vs, mm)
        io.Vs = sorted([0.0, io.Veff - io.Vp - io.TAW, io.DAW])[1]
        # Residual soil moisture (Vr, mm)
        io.Vr = sorted([0.0, io.Veff - io.Vp - io.Vs, io.TAW])[1]

        # Deep percolation: If drainable water available
        io.DP = sorted([0.0, io.Vs + io.Vp, io.K])[1]

        #Root zone saturated soil water depletion (Ds,mm)
        io.Ds = max(0.0, io.DAW - io.Vs)
        #Root zone residual soil water depletion (Dr,mm)
        io.Dr = max(0.0, io.TAW - io.Vr)

        #Root zone soil water depletion fraction (fDr, mm/mm)
        io.fDr = 1.0 - ((io.TAW - io.Dr) / io.TAW)

        #Saturation zone soil water depletion fraction (fDr, mm/mm)
        io.fDs = 1.0 - ((io.DAW - io.Ds) / io.DAW)

        io.theta0 = io.Veff / (1000*io.Zp) + io.thetaWP
