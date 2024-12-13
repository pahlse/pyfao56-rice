# Soil Water Balance Adaptation for Paddy Fields (FAO56)

Author: Elias Pahls Version: 13/12/2024

## Initial Concept and Methodology

Originaly FAO56 assumes that following a heavy rain or irrigation turn all
water above field capacity is lost to percolation on the same day. For paddy
conditions this is problematic, because traditionally a puddle is established
through land preparation called "puddling" which significantly reduces
percolation. A perched water table is then maintained in the field for optimal
plant growth. For the soil water balance this means that field conditions are
kept at or above saturation with continuous percolation throught most of the
season. To properly account for all the water in the paddy the fao56 methodlogy
has to be expanded beyond `TAW`, `RAW` and `Dr`:

### Water Storage Potentials:
- **Root Zone Drainable Dater (DAW):**  Full Saturation to Field Capacity.
- **Standing Water Above Ground:** Ponding or surface water limited by bund hight
 
### Depletion:
- **Depletion of Saturation (Ds):** 

### Dynamic Water Content in Paddy:
- **Total Water in Puddle (Veff):**
- **Ponding Depth (Vp):**
- **Saturation Depth (Vs):** 
- **Residual Soil Moisture (Vr):**

In order to calculate Dr and Ds ()

The methodology follows a daily water balance approach:
- Compute **Initial Available Soil Moisture (`Vini`)**.
- Separate water into the three buckets: root zone (`Vr`), saturation zone
  (`Vs`), and ponding (`Vp`).
- Incorporate **Irrigation Losses** and **Effective Irrigation (`effirr`)**.
- Compute **Runoff** based on bund height and ponding conditions.
- Compute **Effective Precipitation (`effrain`)**.

### Categories in the Water Balance
1. **Potential Water Storage:** (`TAW`, `DAW`).
2. **Depletion:** (`Dr`).
3. **Dynamic Daily Components:** (`Vini`, `Vr`, `Vs`).

---

## Key Additions and Improvements

### 1. Incorporating Bund Height and Runoff Mechanisms
- Added logic for **runoff** due to rainfall and irrigation exceeding the bund
  height.
- Separated runoff contributions into:
  - **Irrigation Runoff (`runoff_irr`)**.
  - **Rainfall Runoff (`runoff_rain`)**.
- Combined these into a total `io.runoff`.

**Example Code:**
```python
runoff_irr = 0.0
runoff_rain = 0.0
if io.ponded is True:
    # Irrigation runoff
    if io.idep + io.Vp > io.Bundh:
        runoff_irr = io.idep + io.Vp - io.Bundh
        io.irrloss += runoff_irr

    # Rainfall runoff
    if io.rain + io.Vp > io.Bundh:
        runoff_rain = io.rain + io.Vp - io.Bundh

# Total runoff
io.runoff += runoff_irr + runoff_rain
