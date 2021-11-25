#################################################################################
######################### figure 2 KM ###########################################
#################################################################################
import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from config import start_date, end_date, today
sys.path.append('lib/')
from functions import *

#specify date columns
date_cols = [
    "date_antigen_negative",
    "date_exposure_to_disease",
    "date_historic_covid",
    "date_potential_historic_covid",
    "date_probable_covid",
    "date_probable_covid_pos_test",
    "date_probable_covid_sequelae",
    "date_suspected_covid_advice",
    "date_suspected_covid_had_test",
    "date_suspected_covid_isolation",
    "date_suspected_covid_nonspecific",
    "date_suspected_covid",
    "date_covid_unrelated_to_case_status",
    "date_sgss_positive_test",
    "date_died_ons"
]

# import data
df = pd.read_csv(
    filepath_or_buffer = 'output/input.csv',    
    parse_dates = date_cols
)

#derive start/end dates
df["start_date"] = df[date_cols].min().min()
df["end_date"] = df[date_cols].max().max()


# derive time-to-event censoring info

# death date or last date of follow up
df['date_event'] = np.where(df['date_died_ons']<=df['end_date'], df['date_died_ons'], df['end_date'])

# censoring indiators
df['indicator_death'] = np.where((df['date_died_ons']<=df['end_date']) & (df['died_ons']==1), 1, 0)
df['indicator_death_covid'] = np.where((df['date_died_ons']<=df['end_date'])  & (df['died_ons_covid']==1), 1, 0)
df['indicator_death_noncovid'] = np.where((df['date_died_ons']<=df['end_date']) & (df['died_ons_noncovid']==1), 1, 0)

# censor death category if end date exceeds last date
df['death_category'] = np.where(df['date_died_ons']<=df['end_date'], df['death_category'], "alive")

# derive time-to-death from positive test date
df['pvetestSGSS_to_death'] = (df['date_event'] - df['date_sgss_positive_test']).astype('timedelta64[D]')
df['pvetestPC_to_death'] = (df['date_event'] - df['date_probable_covid_pos_test']).astype('timedelta64[D]')

## positive test as indicated in SGSS or in primary care
df_pvetestSGSS = df[~np.isnan(df['date_sgss_positive_test'])]
df_pvetestPC = df[~np.isnan(df['date_probable_covid_pos_test'])]


fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(10,5), sharey=True)

# SGSS pos test to death
kmdata = KMestimate(df_pvetestSGSS['pvetestSGSS_to_death'], df_pvetestSGSS['indicator_death'])
kmdata_covid = KMestimate(df_pvetestSGSS['pvetestSGSS_to_death'], df_pvetestSGSS['indicator_death_covid'])
kmdata_noncovid = KMestimate(df_pvetestSGSS['pvetestSGSS_to_death'], df_pvetestSGSS['indicator_death_noncovid'])

axes[0].step(kmdata_covid['times'], 1-kmdata_covid['kmestimate'], label='covid deaths') 
axes[0].step(kmdata_noncovid['times'], 1-kmdata_noncovid['kmestimate'], label = 'non-covid deaths')
axes[0].set_xlabel('Days')
axes[0].set_ylabel('1 - KM survival estimate')
axes[0].set_title("as identified from SGSS data\n")
axes[0].legend()
axes[0].set_xlim(0, 80)

# PC pos test to death
kmdata = KMestimate(df_pvetestPC['pvetestPC_to_death'], df_pvetestPC['indicator_death'])
kmdata_covid = KMestimate(df_pvetestPC['pvetestPC_to_death'], df_pvetestPC['indicator_death_covid'])
kmdata_noncovid = KMestimate(df_pvetestPC['pvetestPC_to_death'], df_pvetestPC['indicator_death_noncovid'])

axes[1].step(kmdata_covid['times'], 1-kmdata_covid['kmestimate'], label='covid deaths') 
axes[1].step(kmdata_noncovid['times'], 1-kmdata_noncovid['kmestimate'], label = 'non-covid deaths')
axes[1].set_xlabel('Days')
axes[1].set_ylabel('1 - KM survival estimate')
axes[1].set_title("as identified from primary care data\n")
axes[1].set_xlim(0, 80)

fig.suptitle("Days from positive test to death", y=1.05, fontsize=14)
fig.tight_layout()
fig.savefig("output/figs.svg")
