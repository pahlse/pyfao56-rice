# pyfao56 Adaptations for Paddy Fields

Author: Elias Pahls\
Date:   18/04/2025

This repository contains a fork of the `pyfao56` package that was developed
in the scope of my MSc [thesis](./docs/MSc.Thesis.Elias.Pahls.Modeling.FAO56.IRRI.India-compact.pdf) at Wageningen University, The Netherlands. The
specific objectives were to adapt the original FAO56 methodology to paddy and
direct-seeded rice conditions based on CROPWAT 8.0 and  [van Genuchten et al. (1980)](./docs/vanGenuchten1980.pdf).[^1] 
Details on the concepts and methods used can be found in Sections 2.2 and 3.2 of
the thesis.

## TL-DR

This package expands on the `pyfao56` package
([kthorp/pyfao56](https://github.com/kthorp/pyfao56)) by implementing most of
the original CROPWAT 8.0 functionalities for paddy conditions and expandes the
original FAO56 methodology by parameterizing hydraulic conductivity `K` based
on van Genuchten et al. (1980)[^1]. The main additions are:

- Daily water balance calculation based on all water in the paddy (surface,
  saturation, root-zone) represented by `Veff`
- Deep percolation based on variable `K` and van Genuchten soil parameters.
- User-definable landpreparation stage in `landprep.py` to calculate water
  requirments for land preparation and establish initial water balance 

A 'working' example can be found in `main.py` to showcase the adaptations.

## Pending Tasks

- [ ] Update README to include all new parameters, describe landprep.py and van
      Genuchten method.
- [ ] Reduce code in main-DSR.py and main-TPR.py to minimal working example.
- [ ] Clean up data and results dirs.

## Concepts and Methodology

Originaly FAO56 assumes that following a heavy rain or irrigation all water
above field capacity is lost to percolation on the same day. For paddy
conditions this is problematic, because traditionally, a puddle is established
through land preparation called "puddling" which significantly reduces
percolation. A perched water table is then maintained in the field for optimal
plant growth. For the soil water balance this means that field conditions are
kept at or above saturation with continuous percolation throught most of the
season. As the pyfao56 package stands now, this condition cannot be represented.

### Defining the Water Balance

To properly account for all the water in the paddy the fao56 methodlogy
has to be expanded beyond the already defined `TAW`, `RAW` and `Dr`. The
following additional parameters are proposed:

#### 1. Water Storage Potentials
- **Root Zone Drainable Water (DAW)**\
  Similar to `TAW`, `DAW` represents all
  potential water storable in the root zone from Saturation to Field Capacity.
 
- **Max Ponding Water** \
  This is the max above-surface water in the paddy and
  is defined by introducing a bund hight `Bundh`.
 
#### 2. Dynamic Water Content in Paddy

Unlike the original FAO56 approach where the root zone depletion `Dr` is
directly calculated from all applicable water balance components the paddy
scenario is more complex. Water can be stored in three distinct storage
components above or below ground (call them 'buckets') which are each governed
by different properties and processes. To model this, total available water
should be established first from where depletion, irrigation requirements, etc
can then be derived. The relevant parameters are:

- **Total Water in Puddle (Veff)**\
  To track how much water is in each respective bucket the total volume of
  water in the paddy is first established. The daily soil water balance is then
  carried out on the base of this `Veff`.
  
- **Ponding Depth (Vp)**\
  A non-zero ponding depth occurs if `Veff > TAW + DAW` (i.e water in the paddy
  exceed saturation) and is limited by `Bundh`. If `Veff` exceeds `Bundh`
  runoff occurs.
  
- **Saturation Depth (Vs)**\
  A non-zero saturation depth occurs if `Veff > Vp + TAW` and is limited by
  `DAW`. Deep percolation occurs as long as `Vs > 0`.
  
- **Residual Soil Moisture (Vr)**\
  Non-zero residual soil moisture occurs if `Veff > Vp + DAW` and is limited by
  `TAW`.

#### 3. Soil Water Depletion

After establishing total avialable water and is subsequent distribution,
depletion in the soil can be defined as follows:

- **Depletion of Saturation (Ds)**\
  Similar to `Dr`, `Ds` is the depletion of saturation in the root zone. It is
  defined as `Ds = DAW - Vs`.
 
- **Root Zone Depletion (Dr)**\
  Since the SWB is already calculated in `Veff`, root zone depletion can be
  expressed as `Dr = TAW - Vr`.

### Calculation Procedure

First, initiate the parameters:

1. Compute available soil moisture `Veff` for day 0 using `landprep.py`.
2. Separate `Veff` into its constituents: root zone `Vr`, saturation zone
  `Vs`, and ponding `Vp`.
3. Derive `Dr` and `Ds`.
 
Next calculate the daily SWB:

1. Compute irrigation requirment based on `Dr` or `Ds` or `Vp`.
2. Compute effective precipitation (`effrain`).
3. Compute runoff based on bund height and ponding conditions.
4. Compute percolation based on `Ksat` and available water above saturation.
5. Add irrigation and raifall quantities to `Veff`
6. Subtract percolation, ETadj, and runoff from `Veff`
7. Separate `Veff` into its constituents: root zone `Vr`, saturation zone
  `Vs`, and ponding `Vp`.
8. Derive `Dr` and `Ds` for the day

## Code Implementation

The following additions to `model.py` are propoesd:

1. Initiation of SWB components in `run()`:
  ```python
  #Initial root zone drainable available water (DAW, mm)
  io.DAW = 1000. * (io.thetaS - io.thetaFC) * io.Zrini

  #Max standing water in filed
  io.Bundh   = self.par.Bundh
  #NOTE: defined by Bundh which was chosen to be set as a variable in parameters.py


  #Initial effective available moisture (Vtot, mm)
  io.Veff = 1000 * (io.theta0 - io.thetaWP) * io.Zrini
  #NOTE: This accounts for all the water in the paddy and can exceed 
  #TAW + DAW, hence the different nomenclature to prevent confusion.

  # Initial ponding depth (Vp, mm)
  io.Vp = sorted([0.0, io.Veff - io.DAW - io.TAW, io.Bundh])[1]
  # Initial saturation depth (Vs, mm)
  io.Vs = sorted([0.0, io.Veff - io.Vp - io.TAW, io.DAW])[1]
  # Initial residual soil moisture (Vr, mm)
  io.Vr = sorted([0.0, io.Veff - io.Vp - io.DAW, io.TAW])[1]
  ```


2. Daily SWB components in `_advance()`:
  ```python
  #Deep percolation (DP, mm) with max percolation being Ksat
  #Boundary layer is considered at the root zone depth (Zr)
  io.DP = sorted([0.0, io.Vs, io.Ksat])[1]

  # Total soil moisture in puddle (Veff, mm)
  io.Veff = io.Veff + effrain + effirr - io.ETcadj - io.DP
  # Ponding depth (Vp, mm)
  io.Vp = sorted([0.0, io.Veff - io.DAW - io.TAW, io.Bundh])[1]
  # Saturation depth (Vs, mm)
  io.Vs = sorted([0.0, io.Veff - io.Vp - io.TAW, io.DAW])[1]
  # Residual soil moisture (Vr, mm)
  io.Vr = sorted([0.0, io.Veff - io.Vp - io.DAW, io.TAW])[1]

  #Root zone saturated soil water depletion (Ds,mm)
  io.Ds = max(0.0, io.DAW - io.Vs)
  #Root zone residual soil water depletion (Dr,mm)
  io.Dr = max(0.0, io.TAW - io.Vr)
  ```

## Scope for Future Work 

- [ ] Replace volumetric water content by matric potential head as the primary
      state variable to calculate `K`, `Dr`, `Ds` etc. This could reduce model complexity.
- [ ] Expand soil conductivity functionality to the `SoilProfile` class to allow
      for spatially variable soil properties and time-varying hydraulic
      conductivity. Might get complicated fast!
- [ ] Integrate `landprep.py` directly into `model.py` instead of calling it
      from `main.py`
- [ ] Include the nursery phase as a seperate module to allow for simulation of
      the entire rice cropping cycle. This could be done based on CROPWAT 8.0
- [ ] Integrate pedotransfer functions (using e.g. the
      [pedon](https://github.com/martinvonk/pedon) python package) to estimate
      soil hydraulic properties from soil texture and bulk density.

## References

[^1]: van Genuchten, M. T. (1980). “A Closed-form Equation for Predicting the Hydraulic
Conductivity of Unsaturated Soils”. In: Soil Science Society of America Journal
44.5. url: http://dx.doi.org/10.2136/sssaj1980.03615995004400050002x.
