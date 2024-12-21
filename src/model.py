import pandas as pd
import datetime
import math

# from .landprep import Landprep

class Model:

    def __init__(self, start, end, par, wth, irr=None, autoirr=None,
                 sol=None, upd=None, ponded=False, puddled=False, roff=False,  #NOTE: 'ponded' functionality not yet implemented
                 cons_p=False, aq_Ks=False, comment=''):

        self.startDate = datetime.datetime.strptime(start, '%Y-%j')
        self.endDate   = datetime.datetime.strptime(end, '%Y-%j')
        self.par = par
        self.wth = wth
        self.irr = irr
        self.autoirr = autoirr
        self.sol = sol
        self.upd = upd
        self.puddled = puddled
        self.ponded = ponded
        self.roff = roff
        self.cons_p = cons_p
        self.aq_Ks = aq_Ks
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
        if self.sol is None:
            solmthd = 'D - Default FAO-56 homogenous soil bucket ' \
                      'approach'
        else:
            solmthd = 'L - Fort Collins ARS stratified soil layers ' \
                      'approach'

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

    def savesummary(self, filepath='pyfao56_summary.out'):
        self.tmstmp = datetime.datetime.now()
        timestamp = self.tmstmp.strftime('%Y-%m-%d %H:%M:%S')
        sdate = self.startDate.strftime('%Y-%m-%d')
        edate = self.endDate.strftime('%Y-%m-%d')

        fmts = {
            'Date': '{:10s}'.format, 'DOY': '{:5d}'.format, 'Day':
            '{:5d}'.format, 'ETref': '{:7.2f}'.format, 'ETc': '{:7.2f}'.format,
            'ETcadj': '{:7.2f}'.format, 'E': '{:7.2f}'.format, 'T':
            '{:7.2f}'.format, 'DP': '{:7.2f}'.format, 'Irrig':
            '{:7.2f}'.format, 'IrrLoss': '{:7.2f}'.format, 'Rain':
            '{:7.2f}'.format, 'Runoff': '{:7.2f}'.format, 'TAW':
            '{:7.2f}'.format, 'DAW': '{:7.2f}'.format, 'RAW': '{:7.2f}'.format,
            'Veff': '{:7.2f}'.format, 'Vp': '{:7.2f}'.format, 'Vs':
            '{:7.2f}'.format, 'Vr': '{:7.2f}'.format, 'Ds': '{:7.2f}'.format,
            'Dr': '{:7.2f}'.format, 'fDr': '{:7.2f}'.format, 'fDs': '{:7.2f}'.format

        }

        keys = [
            'Date', 'DOY', 'Day', 'ETref', 'ETc', 'ETcadj', 'E', 'T', 'DP',
            'Irrig', 'IrrLoss', 'Rain', 'Runoff', 'TAW', 'DAW', 'RAW',
            'Veff', 'Vp', 'Vs', 'Vr', 'Ds', 'Dr', 'fDr', 'fDs'
        ]

        ast = '*' * 72
        s = (
            f'{ast}\n'
            'pyfao56: FAO-56 Evapotranspiration in Python\n'
            'Summary of Selected Data\n'
            f'Timestamp: {timestamp}\n'
            f'Simulation start date: {sdate}\n'
            f'Simulation end date: {edate}\n'
            f'{ast}\n'
        )

        # Header for selected keys
        header = (
            f'{keys[0]:>10s}'  # Date
            f'{keys[1]:>6s}'   # DOY
            f'{keys[2]:>6s}'   # Day
            + ''.join(f'{key:>8s}' for key in keys[3:])
        )

        s += header + '\n'

        # Check if odata is not empty and write formatted rows
        if not self.odata.empty:
               for _, row in self.odata.iterrows():
                   formatted_row = ' '.join(
                       fmts[key](int(row[key]) if key in ['DOY', 'Day'] else row[key])
                       if key in fmts and pd.notnull(row[key]) else str(row[key])
                       for key in keys if key in self.odata.columns
                   )
                   s += formatted_row + '\n'

        try:
            with open(filepath, 'w') as f:
                f.write(s)
                print(f"Summary successfully saved to {filepath}")
        except FileNotFoundError:
            print('The filepath for the summary data is not found.')

    def savecsv(self, filepath='pyfao56_summary.csv'):
        keys = [ 'Date', 'DOY', 'Day', 'ETref', 'ETc', 'ETcadj', 'E', 'T',
                'DP', 'Irrig', 'IrrLoss', 'Rain', 'Runoff', 'TAW', 'DAW',
                'RAW', 'Veff', 'Vp', 'Vs', 'Vr', 'Ds', 'Dr', 'fDr', 'fDs' ]

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
            keys = [ 'ETref', 'ETc', 'ETcadj', 'E', 'T', 'DP', 'K', 'Rain',
                    'Runoff', 'Irrig', 'IrrLoss', 'Gross_Irrig', 'Num_Irrig',
                    'Mean_Irrig', 'Dr_ini', 'Dr_end', 'Veff_ini', 'Veff_end' ]
            for key in keys:
                s += '{:8.3f} : {:s}\n'.format(self.swbdata[key],key)

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
        io.Kcbini  = self.par.Kcbini
        io.Kcbmid  = self.par.Kcbmid
        io.Kcbend  = self.par.Kcbend
        io.Lini    = self.par.Lini
        io.Ldev    = self.par.Ldev
        io.Lmid    = self.par.Lmid
        io.Lend    = self.par.Lend
        io.hini    = self.par.hini
        io.hmax    = self.par.hmax
        io.thetaFC = self.par.thetaFC
        io.thetaWP = self.par.thetaWP
        io.theta0  = self.par.theta0
        io.thetaS  = self.par.thetaS
        io.Wdpud   = self.par.Wdpud
        io.Ksat    = self.par.Ksat
        io.Zrini   = self.par.Zrini
        io.Zrmax   = self.par.Zrmax
        io.Bundh   = self.par.Bundh * 1000
        io.pbase   = self.par.pbase
        io.Ze      = self.par.Ze
        io.REW     = self.par.REW
        io.CN2     = float(self.par.CN2)
        if self.sol is None:
            io.solmthd = 'D' #Default homogeneous soil from Parameters
            #Total evaporable water (TEW, mm) - FAO-56 Eq. 73
            io.TEW = 1000. * (io.thetaFC - 0.50 * io.thetaWP) * io.Ze
            #Initial depth of evaporation (De, mm) - FAO-56 page 153
            io.De = 1000. * (io.thetaFC - 0.50 * io.thetaWP) * io.Ze
            #Initial root zone depletion (Dr, mm) - FAO-56 Eq. 87
            io.Dr = 1000. * (io.thetaFC - io.theta0) * io.Zrini
            #Initial root zone residual available water (TAW, mm)
            io.TAW = 1000. * (io.thetaFC - io.thetaWP) * io.Zrini
            #By default, FAO-56 doesn't consider the following variables

            io.l = 0.50
            io.n = 1.3055
            io.m = 1 - 1/io.n
            io.thetaR = 0.0971

            io.Se = sorted([0, (io.theta0 - io.thetaWP)/ (io.thetaS - io.thetaWP), 1])[1]
            # io.K = sorted([0, io.Ksat * io.Se**0.5 * (1 - (1 - io.Se**(1/io.m))**io.m)**2, io.Ksat])[1]
            io.K = io.Ksat


            io.DAW = 0
            io.Veff = 0
            io.Vp = 0
            io.Vs = 0
            io.Vr = 0
            io.Ds = 0



            # --- Initial Rice Settings ---------------------------------
            if self.ponded:
                #Initial root zone drainable available water (DAW, mm)
                io.DAW = 1000. * (io.thetaS - io.thetaFC) * io.Zrini

                io.DP = 0

                #Initial effective available moisture (Vtot, mm)
                #NOTE: This accounts for all the water in the paddy and can exceed 
                #TAW + DAW, hence the different nomenclature to prevent confusion.
                io.Veff = 1000 * (io.theta0 - io.thetaWP) * io.Zrini
                # Initial ponding depth (Vp, mm)
                io.Vp = sorted([0.0, io.Veff - io.DAW - io.TAW, io.Bundh])[1]
                # Initial saturation depth (Vs, mm)
                io.Vs = sorted([0.0, io.Veff - io.Vp - io.TAW, io.DAW])[1]
                # Initial residual soil moisture (Vr, mm)
                io.Vr = sorted([0.0, io.Veff - io.Vp - io.Vs, io.TAW])[1]

                io.Ds = sorted([0.0, io.DAW - io.Vp, io.Bundh])[1]

        #Initial root zone soil water depletion fraction (fDr, mm/mm)
        io.fDr = 1.0 - ((io.TAW - io.Dr) / io.TAW)
        io.fDs = 1.0 - ((io.DAW - io.Ds) / io.DAW)
        io.Ks = 1.0
        io.h = io.hini
        io.Zr = io.Zrini
        io.fw = 1.0
        io.wndht  = self.wth.wndht
        io.rfcrp  = self.wth.rfcrp
        io.ponded = self.ponded
        io.puddled = self.puddled
        io.roff   = self.roff
        io.cons_p = self.cons_p
        io.aq_Ks  = self.aq_Ks
        self.odata = pd.DataFrame(columns=self.cnames)

        # # Perform land preparation if puddled
        # if self.puddled:
        #     print("Starting land preparation phase...")

        #     while io.i <= self.par.Lprp:
        #         mykey = tcurrent.strftime('%Y-%j')  # Generate key for the current date

        #        self.Landprep(io)  # Run the advance method for land preparation

        #         tcurrent += tdelta  # Update the global simulation date
        #         io.i += 1  # Increment the day counter
        #         print(f"Land preparation day {io.i} completed, Date: {tcurrent.strftime('%Y-%m-%d')}")

        #     print("Land preparation phase completed.")

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
            if self.irr is not None:
                if mykey in self.irr.idata.index:
                    io.idep = self.irr.idata.loc[mykey,'Depth']
                    io.fw = self.irr.idata.loc[mykey,'fw']
                    io.ieff = self.irr.idata.loc[mykey,'ieff']

            #Evaluate autoirrigation conditions and compute amounts
            if self.autoirr is not None:
                for i in range(self.autoirr.aidata.shape[0]):
                    #Evaluate date range condition
                    aistart= self.autoirr.aidata.loc[i,'start']
                    aistart= datetime.datetime.strptime(aistart,'%Y-%j')
                    aiend  = self.autoirr.aidata.loc[i,'end']
                    aiend  = datetime.datetime.strptime(aiend,'%Y-%j')
                    if tcurrent<aistart or tcurrent>aiend: 
                        continue # NOTE: Continue continues to next itteration
                                 # of loop; i.e. next row.

                    #Evaluate "after last recorded irrigation" condition
                    if self.autoirr.aidata.loc[i,'alre']:
                        if self.irr is not None:
                            lastirr = self.irr.getlastdate()
                            if tcurrent <= lastirr:
                                continue

                    #Evaluate forecasted precipitation condition
                    fpdep = self.autoirr.aidata.loc[i,'fpdep']
                    fpday = int(self.autoirr.aidata.loc[i,'fpday'])
                    fpact = self.autoirr.aidata.loc[i,'fpact']
                    fcrain = 0.
                    for j in range(fpday):
                        fpdate = tcurrent + j*tdelta
                        fpkey = fpdate.strftime('%Y-%j')
                        fcrain += self.wth.wdata.loc[fpkey,'Rain']
                    reduceirr = 0.
                    if fcrain >= fpdep:
                        if fpact == 'cancel':
                            continue
                        elif fpact == 'reduce':
                            reduceirr = fcrain
                        elif fpact not in ['proceed']:
                            continue
                    
                    #Evaluate management allowed depletion (mm/mm)
                    if io.fDs <= self.autoirr.aidata.loc[i,'madDs']:
                        continue
                    if io.fDr <= self.autoirr.aidata.loc[i,'mad']:
                        continue
                    if io.Dr >= self.autoirr.aidata.loc[i,'madDr']:
                        continue
                    if io.Vp >= self.autoirr.aidata.loc[i,'madVp']:
                        continue
                    #Evaluate critical Ks
                    if io.Ks >= self.autoirr.aidata.loc[i,'ksc']:
                        continue

                    #Evaluate days since last irrigation (dsli)
                    idays = self.odata[self.odata['Irrig']>0.]
                    idays = pd.to_datetime(idays.index,format='%Y-%j')
                    if idays.size > 0:
                        dsli = (tcurrent-max(idays)).days
                    else:
                        dsli = ((tcurrent-self.startDate).days)+1
                    if dsli < self.autoirr.aidata.loc[i,'dsli']:
                        continue
                    
                    #Evaluate days since last watering event
                    evnt = self.autoirr.aidata.loc[i,'evnt']
                    edays = self.odata[(self.odata['Irrig']-
                                        self.odata['IrrLoss']+
                                        self.odata['Rain']-
                                        self.odata['Runoff'])>=evnt]
                    edays = pd.to_datetime(edays.index,format='%Y-%j')
                    if edays.size > 0:
                        dsle = (tcurrent-max(edays)).days
                    else:
                        dsle = ((tcurrent-self.startDate).days)+1
                    if dsle < self.autoirr.aidata.loc[i,'dsle']:
                        continue

                    #All conditions were met, need to autoirrigate
                    #Default rate is root-zone soil water depletion (Dr)
                    # rate = max([0.0,io.Dr + io.Ds - reduceirr])

#-------------------------------------------------------------------------
                    #NOTE: This is not working as desird. Vp gets triggered, but rate 

                    rate = max([0.0,io.Dr + io.Ds * 0.8 - reduceirr])
                    # wdpth = self.autoirr.aidata.loc[i,'wdpth']
                    # rate = max([0.0, io.Dr + io.Ds + wdpth - reduceirr])

                    if io.fDs >= self.autoirr.aidata.loc[i,'madDs']:
                        wdpth = self.autoirr.aidata.loc[i,'wdpth']
                        rate = max([0.0, io.Dr + io.Ds + wdpth - reduceirr])

                    if io.Vp <= self.autoirr.aidata.loc[i,'madVp']:
                        wdpth = self.autoirr.aidata.loc[i,'wdpth']
                        rate = max([0.0, io.Dr + io.Ds + wdpth - reduceirr])

#-------------------------------------------------------------------------

                    #Alternatively, the default rate may be modified:
                    #Use a contant rate
                    icon  = self.autoirr.aidata.loc[i,'icon']
                    if not math.isnan(icon):
                        rate = max([0.0, icon - reduceirr])
                    #Target a specific root-zone soil water depletion
                    itdr  = self.autoirr.aidata.loc[i,'itdr']
                    if not math.isnan(itdr):
                        rate = max([0.0,io.Dr - reduceirr - itdr])
                    #Target a fractional root-zone soil water depletion
                    itfdr = self.autoirr.aidata.loc[i,'itfdr']
                    if not math.isnan(itfdr):
                        itdr2 = io.TAW-io.TAW*(1.0-itfdr)
                        rate = max([0.0,io.Dr - reduceirr - itdr2])


                    #Update fraction wetted (fw) for autoirrigation
                    io.fw=self.autoirr.aidata.loc[i,'fw']

                    #Specify the final autoirrigation rate
                    io.idep=rate
                    break

            #Obtain updates for Kcb, h, and fc, if available
            io.updKcb = float('NaN')
            io.updh = float('NaN')
            io.updfc = float('NaN')
            if self.upd is not None:
                io.updKcb = self.upd.getdata(mykey,'Kcb')
                io.updh = self.upd.getdata(mykey,'h')
                io.updfc = self.upd.getdata(mykey,'fc')

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

        #Save seasonal water balance data to self.swbdata dictionary
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

        #Basal crop coefficient (Kcb)
        #From FAO-56 Tables 11 and 17
        s1 = io.Lini
        s2 = s1 + io.Ldev
        s3 = s2 + io.Lmid
        s4 = s3 + io.Lend
        if 0<=io.i<=s1:
            io.tKcb = io.Kcbini
            io.Kcb = io.Kcbini
        elif s1<io.i<=s2:
            io.tKcb += (io.Kcbmid-io.Kcbini)/(s2-s1)
            io.Kcb += (io.Kcbmid-io.Kcbini)/(s2-s1)
        elif s2<io.i<=s3:
            io.tKcb = io.Kcbmid
            io.Kcb = io.Kcbmid
        elif s3<io.i<=s4:
            io.tKcb += (io.Kcbmid-io.Kcbend)/(s3-s4)
            io.Kcb += (io.Kcbmid-io.Kcbend)/(s3-s4)
        elif s4<io.i:
            io.tKcb = io.Kcbend
            io.Kcb = io.Kcbend
        #Overwrite Kcb if updates are available
        if io.updKcb > 0: io.Kcb = io.updKcb

        #Plant height (h, m)
        io.h = max([io.hini+(io.hmax-io.hini)*(io.Kcb-io.Kcbini)/
                    (io.Kcbmid-io.Kcbini),0.001,io.h])

        #Overwrite h if updates are available
        if io.updh > 0: io.h = io.updh

        # ------------------------------------------------
        # NOTE: This should be double checked with Gerardo
        # ------------------------------------------------

        #Root depth (Zr, m) - FAO-56 page 279; based on Kc <- pyfao original Method
        # io.Zr = max([io.Zrini + (io.Zrmax-io.Zrini)*(io.tKcb-io.Kcbini)/
        #              (io.Kcbmid-io.Kcbini),0.001,io.Zr])
        
        #Root depth (Zr, m) - FAO-56 page 279; based on DOY <- CROPWAT method
        if io.Zr < io.Zrmax and not io.puddled:
            io.Zr = max([io.Zrini + (io.Zrmax-io.Zrini)*io.i/
                       (io.Lini + io.Ldev),0.001,io.Zr])
        else:
            io.Zr = io.Zrmax

        #Upper limit crop coefficient (Kcmax) - FAO-56 Eq. 72
        u2 = io.wndsp * (4.87/math.log(67.8*io.wndht-5.42))
        u2 = sorted([1.0,u2,6.0])[1]
        rhmin = sorted([20.0,io.rhmin,80.0])[1]
        if io.rfcrp == 'S':
            io.Kcmax = max([1.2+(0.04*(u2-2.0)-0.004*(rhmin-45.0))*
                            (io.h/3.0)**.3, io.Kcb+0.05])
        elif io.rfcrp == 'T':
            io.Kcmax = max([1.0, io.Kcb + 0.05])

        #Canopy cover fraction (fc, 0.0-0.99) - FAO-56 Eq. 76
        io.fc = sorted([0.0,((io.Kcb-io.Kcbini)/(io.Kcmax-io.Kcbini))**
                        (1.0+0.5*io.h),0.99])[1]

        
        #Overwrite fc if updates are available
        if io.updfc > 0: io.fc = io.updfc

        #Losses due to irrigation inefficiency (irrloss, mm)
        io.irrloss = io.idep * (1 - io.ieff / 100.)

        # Surface runoff (runoff, mm)
        io.runoff = 0.0
        runoff_irr = 0.0
        runoff_rain = 0.0

        if io.roff is True:
            #Method per ASCE (2016) Eqs. 14-12 to 14-20, page 451-454
            CN1 = io.CN2/(2.281-0.01281*io.CN2) #ASCE (2016) Eq. 14-14
            CN3 = io.CN2/(0.427+0.00573*io.CN2) #ASCE (2016) Eq. 14-15
            if io.De <= 0.5*io.REW:
                CN = CN3 #ASCE (2016) Eq. 14-18
            elif io.De >= 0.7*io.REW+0.3*io.TEW:
                CN = CN1 #ASCE (2016) Eq. 14-19
            else:
                CN = (io.De-0.5*io.REW)*CN1
                CN = CN+(0.7*io.REW+0.3*io.TEW-io.De)*CN3
                CN = CN/(0.2*io.REW+0.3*io.TEW) #ASCE (2016) Eq. 14-20
            storage = 250.*((100./CN)-1.) #ASCE (2016) Eq. 14-12
            if io.rain > 0.2*storage:
                #ASCE (2016) Eq. 14-13
                io.runoff = (io.rain-0.2*storage)**2
                io.runoff = io.runoff/(io.rain+0.8*storage)
                io.runoff = min([io.runoff,io.rain])
            else:
                io.runoff = 0.0

#------------------------------------------------------------------------
            #Naive implementation of runoff under ponding conditions
            #Will definatly fail in edge cases; e.g. where irrigation and 
            #rain occur on the same day. Definatly needs work!
            if io.ponded is True:
                #Irrigation runoff (mm)
                if io.idep + io.Vp > io.Bundh:
                    runoff_irr = io.idep + io.Vp - io.Bundh
                    io.irrloss += runoff_irr
                #Percipitation runoff (mm)
                if io.rain + io.Vp > io.Bundh:
                    runoff_rain = io.rain + io.Vp - io.Bundh
                    io.runoff = runoff_rain

        #Effective irrigation (mm)
        effirr = max(0, io.idep - io.irrloss)

        #Effective precipitation (mm)
        effrain = max(0, io.rain - io.runoff)
        
        #Total Runoff (mm) accounting for irrigation and rain runoff
        io.runoff = runoff_irr + runoff_rain
#------------------------------------------------------------------------

        #Fraction soil surface wetted (fw) - FAO-56 Table 20, page 149
        if io.idep > 0.0 and io.rain > 0.0:
            pass #fw=fw input
        elif io.idep > 0.0 and io.rain <= 0.0:
            pass #fw=fw input
        elif io.idep <= 0.0 and io.rain >= 3.0:
            io.fw = 1.0
        else:
            pass #fw = previous fw

        # Explenation: This secion calculates the relative contribution of E
        # and T to ETc by determining Kc and Ke from fraction exposed & wetted
        # soil (few), and how much water is evaporable in the topsiol (Kr).

        #Exposed & wetted soil fraction (few, 0.01-1.0) - FAO-56 Eq. 75
        io.few = sorted([0.01,min([1.0-io.fc, io.fw]),1.0])[1]

        #Evaporation reduction coefficient (Kr, 0-1) - FAO-56 Eq. 74
        io.Kr = sorted([0.0,(io.TEW-io.De)/(io.TEW-io.REW),1.0])[1]

        #Evaporation coefficient (Ke) - FAO-56 Eq. 71
        io.Ke = min([io.Kr*(io.Kcmax-io.Kcb), io.few*io.Kcmax])

        #Soil water evaporation (E, mm) - FAO-56 Eq. 69
        io.E = io.Ke * io.ETref

        # NOTE: DPe is used for De and De is used for Kr further up. They
        # reference eachother!

        #Deep percolation under exposed soil (DPe, mm) - FAO-56 Eq. 79
        DPe = effrain + effirr/io.fw - io.De
        io.DPe = sorted([0.0, DPe, io.K])[1]

        #Cumulative depth of evaporation (De, mm) - FAO-56 Eqs. 77 & 78
        De = io.De - effrain - effirr/io.fw + io.E/io.few + io.DPe
        io.De = sorted([0.0,De,io.TEW])[1]

        #Crop coefficient (Kc) - FAO-56 Eq. 69
        io.Kc = io.Ke + io.Kcb

        #Non-stressed crop evapotranspiration (ETc, mm) - FAO-56 Eq. 69
        io.ETc = io.Kc * io.ETref

        if io.solmthd == 'D':
            # Total available water (TAW, mm) - FAO-56 Eq. 82
            io.TAW = 1000.0 * (io.thetaFC - io.thetaWP) * io.Zr

            if self.ponded:
                #Root zone drainable available water (DAW, mm)
                io.DAW = 1000. * (io.thetaS - io.thetaFC) * io.Zr

        #Fraction depleted TAW (p, 0.1-0.8) - FAO-56 p162 and Table 22
        if io.cons_p is True:
            io.p = io.pbase
        else:
            io.p = sorted([0.1,io.pbase+0.04*(5.0-io.ETc),0.8])[1]

        #Readily available water (RAW, mm) - FAO-56 Equation 83
        # io.RAW = io.p * io.TAW
        io.RAW = io.p * io.DAW

        #Transpiration reduction factor (Ks, 0.0-1.0)
        if io.aq_Ks is True:
            #Ks method from AquaCrop
            rSWD = io.Dr/io.TAW
            Drel = (rSWD-io.p)/(1.0-io.p)
            sf = 1.5
            aqKs = 1.0-(math.exp(sf*Drel)-1.0)/(math.exp(sf)-1.0)
            io.Ks = sorted([0.0, aqKs, 1.0])[1]
        else:
            #FAO-56 Eq. 84
            io.Ks = sorted([0.0,(io.TAW-io.Dr)/(io.TAW-io.RAW),1.0])[1]

        #Adjusted crop coefficient (Kcadj) - FAO-56 Eq. 80
        io.Kcadj = io.Ks * io.Kcb + io.Ke

        #Adjusted crop evapotranspiration (ETcadj, mm) - FAO-56 Eq. 80
        io.ETcadj = io.Kcadj * io.ETref

        #Adjusted crop transpiration (T, mm)
        io.T = (io.Ks * io.Kcb) * io.ETref
        
        # # Modify Ksat based on vanGenuchten and previous Theta0
        # io.theta0 = io.Veff/(1000*io.Zr) + io.thetaWP
        # io.Se = sorted([0, (io.theta0 - io.thetaWP)/ (io.thetaS - io.thetaWP), 1])[1]
        # io.K = sorted([0, io.Ksat * io.Se**0.5 * (1 - (1 - io.Se**(1/io.m))**io.m)**2, io.Ksat])[1]

        #Water balance methods
        if io.solmthd == 'D':
            if self.ponded:


                # Total soil moisture in puddle (Veff, mm)
                Veff = io.Veff + effrain + effirr - io.ETcadj - io.DP
                io.Veff = max([Veff, 0.0])

                # Ponding depth (Vp, mm)
                io.Vp = sorted([0.0, io.Veff - io.DAW - io.TAW, io.Bundh])[1]
                # Saturation depth (Vs, mm)
                io.Vs = sorted([0.0, io.Veff - io.Vp - io.TAW, io.DAW])[1]
                # Residual soil moisture (Vr, mm)
                io.Vr = sorted([0.0, io.Veff - io.Vp - io.Vs, io.TAW])[1]

                # Deep percolation: If drainable water in
                io.DP = sorted([0.0, io.Vs, io.K])[1]

                #Root zone saturated soil water depletion (Ds,mm)
                io.Ds = max(0.0, io.DAW - io.Vs)
                #Root zone residual soil water depletion (Dr,mm)
                io.Dr = max(0.0, io.TAW - io.Vr)

#--- Original Code --------------------------------------------------------
            else:
                #Deep percolation (DP, mm) - FAO-56 Eq. 88
                #Boundary layer is considered at the root zone depth (Zr)
                DP = effrain + effirr - io.ETcadj - io.Dr
                io.DP = sorted([0.0,DP,io.K])[1]

                #Root zone soil water depletion (Dr,mm) - FAO-56 Eqs.85 & 86
                Dr = io.Dr - effrain - effirr + io.ETcadj + io.DP
                io.Dr = sorted([0.0, Dr, io.TAW])[1]

            #Root zone soil water depletion fraction (fDr, mm/mm)
            io.fDr = 1.0 - ((io.TAW - io.Dr) / io.TAW)

            #Saturation zone soil water depletion fraction (fDr, mm/mm)
            io.fDs = 1.0 - ((io.DAW - io.Ds) / io.DAW)

            io.theta0 = io.Veff / (1000*io.Zr) + io.thetaWP

