# figure 2 KM
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from config import n

sys.path.append("lib/")
from functions import *
from statsmodels.nonparametric.smoothers_lowess import lowess

# import data
df = pd.read_feather("output/input.feather")

# derive start/end dates
df["start_date"] = df[[col for col in df.columns if col.endswith("_date")]].min().min()
df["end_date"] = df[[col for col in df.columns if col.endswith("_date")]].max().max()

# derive time-to-event censoring info

# death date or last date of follow up
df["date_event"] = np.where(
    df["date_died_ons"] <= df["end_date"], df["date_died_ons"], df["end_date"]
)

# censoring indiators
df["indicator_death"] = np.where(
    (df["date_died_ons"] <= df["end_date"]) & (df["died_ons"] == 1), 1, 0
)
df["indicator_death_covid"] = np.where(
    (df["date_died_ons"] <= df["end_date"]) & (df["died_ons_covid"] == 1), 1, 0
)
df["indicator_death_noncovid"] = np.where(
    (df["date_died_ons"] <= df["end_date"]) & (df["died_ons_noncovid"] == 1), 1, 0
)

# censor death category if end date exceeds last date
df["death_category"] = np.where(
    df["date_died_ons"] <= df["end_date"], df["death_category"], "alive"
)

# list occurances of +ve SGSS tests and proabable +ve covid tests
pos_tests = ["probable_covid_pos_test", "sgss_positive_test"]
df_pos_tests = pd.DataFrame(np.nan, index=range(1, n + 1), columns=pos_tests)
for list in pos_tests:
    for i in range(1, n + 1):
        df_pos_tests[list][i] = f"{list}_X{i}_date"

## positive test as indicated in SGSS or in primary care
df_pvetestPC = pd.melt(
    df,
    id_vars=[
        "date_event",
        "indicator_death",
        "indicator_death_covid",
        "indicator_death_noncovid",
    ],
    value_name="date_probable_covid_pos_test",
    value_vars=df_pos_tests["probable_covid_pos_test"],
)
df_pvetestSGSS = pd.melt(
    df,
    id_vars=[
        "date_event",
        "indicator_death",
        "indicator_death_covid",
        "indicator_death_noncovid",
    ],
    value_name="date_sgss_positive_test",
    value_vars=df_pos_tests["sgss_positive_test"],
)

# derive time-to-death from positive test date
df_pvetestSGSS["pvetestSGSS_to_death"] = (
    df_pvetestSGSS["date_event"] - df_pvetestSGSS["date_sgss_positive_test"]
).astype("timedelta64[D]")
df_pvetestPC["pvetestPC_to_death"] = (
    df_pvetestPC["date_event"] - df_pvetestPC["date_probable_covid_pos_test"]
).astype("timedelta64[D]")

## remove those without a positive test
df_pvetestSGSS = df_pvetestSGSS[~np.isnan(df_pvetestSGSS["date_sgss_positive_test"])]
df_pvetestPC = df_pvetestPC[~np.isnan(df_pvetestPC["date_probable_covid_pos_test"])]

fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(10, 5), sharey=True)

# SGSS pos test to death

kmdata = KMestimate(
    df_pvetestSGSS["pvetestSGSS_to_death"], df_pvetestSGSS["indicator_death"]
)
kmdata_covid = KMestimate(
    df_pvetestSGSS["pvetestSGSS_to_death"], df_pvetestSGSS["indicator_death_covid"]
)
kmdata_noncovid = KMestimate(
    df_pvetestSGSS["pvetestSGSS_to_death"], df_pvetestSGSS["indicator_death_noncovid"]
)

# add smoothing
def smoothing(df):
    x = df["times"]
    y1 = df["kmestimate"]
    smooth = lowess(y1, x, is_sorted=True, frac=0.025, it=0)
    df["kmestimate"] = smooth[:, 1]


smoothing(kmdata_covid)
smoothing(kmdata_noncovid)

axes[0].plot(
    kmdata_covid["times"], 1 - kmdata_covid["kmestimate"], label="covid deaths"
)
axes[0].plot(
    kmdata_noncovid["times"],
    1 - kmdata_noncovid["kmestimate"],
    label="non-covid deaths",
)
axes[0].set_xlabel("Days")
axes[0].set_ylabel("1 - KM survival estimate")
axes[0].set_title("as identified from SGSS data\n")
axes[0].legend()
axes[0].set_xlim(0, 80)

# PC pos test to death
kmdata = KMestimate(df_pvetestPC["pvetestPC_to_death"], df_pvetestPC["indicator_death"])
kmdata_covid = KMestimate(
    df_pvetestPC["pvetestPC_to_death"], df_pvetestPC["indicator_death_covid"]
)
kmdata_noncovid = KMestimate(
    df_pvetestPC["pvetestPC_to_death"], df_pvetestPC["indicator_death_noncovid"]
)

# add smoothing
smoothing(kmdata_covid)
smoothing(kmdata_noncovid)

axes[1].plot(
    kmdata_covid["times"], 1 - kmdata_covid["kmestimate"], label="covid deaths"
)
axes[1].plot(
    kmdata_noncovid["times"],
    1 - kmdata_noncovid["kmestimate"],
    label="non-covid deaths",
)
axes[1].set_xlabel("Days")
axes[1].set_ylabel("1 - KM survival estimate")
axes[1].set_title("as identified from primary care data\n")
axes[1].set_xlim(0, 80)

fig.suptitle("Days from positive test to death", y=1.05, fontsize=14)
fig.tight_layout()
fig.savefig("output/figs.svg")
