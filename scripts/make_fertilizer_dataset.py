"""OPTIONAL experiment: builds data/synthetic/Fertilizer_rule_based.csv from soil-test rules.
The real Kaggle file (irakozekelly/fertilizer-prediction) has labels unrelated to the features
(every model scores ~14% = chance), so this generates a SYNTHETIC but learnable dataset: the fertilizer is the one whose N-P-K profile best
matches the soil's nutrient deficit for the crop. 5% label noise keeps it realistic."""
import numpy as np, pandas as pd

N = 5000
SOILS = ["Sandy", "Loamy", "Black", "Red", "Clayey"]
CROPS = ["Maize", "Sugarcane", "Cotton", "Tobacco", "Paddy", "Barley", "Wheat", "Millets", "Oil seeds", "Pulses", "Ground Nuts"]
FERTS = ["Urea", "DAP", "14-35-14", "28-28", "17-17-17", "20-20", "10-26-26"]
LOW = 20  # soil-test level below which a nutrient counts as deficient

def rule(n, p, k):
    """Standard soil-test logic: supply whichever nutrients are deficient; severity picks the strength."""
    lowN, lowP, lowK = n < LOW, p < LOW, k < LOW
    if lowN and lowP and lowK or lowN and lowK: return "17-17-17"
    if lowN and lowP: return "28-28" if n < 10 and p < 10 else "20-20"
    if lowN: return "Urea"
    if lowP and lowK: return "10-26-26"
    if lowP: return "DAP" if p < 10 else "14-35-14"
    if lowK: return "10-26-26"
    return "17-17-17"  # nothing deficient -> balanced maintenance dose

def build(n=N):
  rng = np.random.default_rng(42)
  rows = []
  for _ in range(n):
      crop = rng.choice(CROPS); soil = rng.choice(SOILS)
      n, p, k = rng.integers(0, 45), rng.integers(0, 45), rng.integers(0, 45)
      f = rule(n, p, k)
      if rng.random() < 0.05:
          f = rng.choice(FERTS)                # label noise
      rows.append([rng.integers(20, 40), rng.integers(40, 80), rng.integers(25, 65), soil, crop, n, k, p, f])

  return pd.DataFrame(rows, columns=["Temperature", "Humidity", "Moisture", "Soil Type", "Crop Type",
                              "Nitrogen", "Potassium", "Phosphorous", "Fertilizer Name"])


if __name__ == "__main__":
    build().to_csv("data/synthetic/Fertilizer_rule_based.csv", index=False)
    print("written", N, "rows")
