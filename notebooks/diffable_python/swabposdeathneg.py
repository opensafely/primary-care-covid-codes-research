# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: all
#     notebook_metadata_filter: all,-language_info
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# + [markdown]
# # COVID-19 and non-COVID-19 mortality following a positive COVID-19 test: analysis of OpenSAFELY data
#
#
# ## Overview
# _Aim_  To investigate COVID-19-related and non-COVID-19 mortality following a COVID-19 positive test. In particular, the potential for overestimation of COVID-19 deaths if all deaths following a positive test are counted as COVID-19 related.
#
# _Data source_  OpenSAFELY. This contains primary care records for every patient registered at a GP practice using TPP's SystmOne health record system. These records are linked with the Second Generation Surveillance System (SGSS) containing information on SARS-CoV-2 viral tests, and with the national death register via the Office for National Statistics (ONS).
#
# _Study population_  All individuals registered at a TPP practice with:
# * a positive SARS-CoV-2 test as recorded in SGSS
# * a positive SARS-CoV-2 test as recorded in their primary care record (containing at least one of these codes: https://codelists.opensafely.org/codelist/opensafely/covid-identification-in-primary-care-probable-covid-positive-test/)
# * a COVID-19 case as recorded in their primary care record (containing at least one of these codes: https://codelists.opensafely.org/codelist/opensafely/covid-identification-in-primary-care-case/)
#
# _Outcomes_  COVID-19 related deaths (defined as a death with the ICD-10 code U071 or U072 anywhere on the death certificate) and non-COVID-19 related deaths (all other registered deaths). For non-COVID related deaths, the primary cause of death is also retrieved.
#
#
# Key variables
# * positive viral test for SARS-CoV2 as indicated in SGSS
# * positive viral or antigen test for SARS-CoV2 as indicated in primary care record
# * COVID-19 case as indicated in primary care record
# * Covid and non-covid death dates as indicated by registered deaths
# -


# ### Import libraries and data
# The dataset used for this report is `/output/input_swabposdeathneg.csv`, created using the study definition `\analysis\study_definintion_swabposdeathneg.py`. The `.csv` file is imported as a pandas dataframe called `df` and is not exposed in the notebook.

# +
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

## import data
df = pd.read_csv(
    #'../output/simulated_input.csv', #dummy data
    '../output/input_swabposdeathneg.csv', #real data
    
    parse_dates=['SGSS_pve_test_date', 'PC_pve_test_date', 'PC_case_date', 'death_date'],
)

## Some data tidying

start_date = pd.to_datetime("2020-02-01", format='%Y-%m-%d')
end_date = pd.to_datetime("2020-07-01", format='%Y-%m-%d')

# replace NaN with ""
df[['sex','region']] = df[['sex','region']].fillna('')
# replace NaN with 0
df[['death','death_anycovid','death_underlyingcovid','death_notanycovid']] = df[['death','death_anycovid','death_underlyingcovid','death_notanycovid']].fillna(0)


## derive some df variables

# censor at censoring date
df['end_date'] = end_date
df['event_date'] = np.where(df['death_date']<=df['end_date'], df['death_date'], df['end_date'])

#df['event_death_anycovid_date'] = np.where((df['death_date']<=df['end_date']) & (df['death_anycovid']==1), df['death_date'], df['end_date'])
#df['event_death_notanycovid_date'] = np.where((df['death_date']<=df['end_date']) & (df['death_notanycovid']==1), df['death_date'], df['end_date'])

df['indicator_death'] = np.where((df['death_date']<=df['end_date']) & (df['death']==1), 1, 0)
df['indicator_death_anycovid'] = np.where((df['death_date']<=df['end_date'])  & (df['death_anycovid']==1), 1, 0)
df['indicator_death_notanycovid'] = np.where((df['death_date']<=df['end_date']) & (df['death_notanycovid']==1), 1, 0)

df['death_category'] = np.where(df['death_date']<=df['end_date'], df['death_category'], "alive")

df['pvetestSGSS_to_death'] = (df['event_date'] - df['SGSS_pve_test_date']).astype('timedelta64[D]')
df['pvetestPC_to_death'] = (df['event_date'] - df['PC_pve_test_date']).astype('timedelta64[D]')
#df['pvetestPC_to_death_anycovid'] = (df['event_death_anycovid_date'] - df['PC_pve_test_date']).astype('timedelta64[D]')
#df['pvetestPC_to_death_notanycovid'] = (df['event_death_notanycovid_date'] - df['PC_pve_test_date']).astype('timedelta64[D]')
df['casePC_to_death'] = (df['event_date'] - df['PC_case_date']).astype('timedelta64[D]')


## positive test as indicated in SGSS or in primary care
df_pvetestSGSS = df.copy()[~np.isnan(df['pvetestSGSS_to_death'])]
df_pvetestPC = df.copy()[~np.isnan(df['pvetestPC_to_death'])]
df_casePC = df.copy()[~np.isnan(df['casePC_to_death'])]

## export ICD10 codes

pd.DataFrame(df['death_underlyingcause'].unique(), columns=['ICD10codes']).to_csv(path_or_buf = "../data/ICD10codes.csv")


# +



# +
## View dataframe 
#print(df)

## check types
print(df.dtypes)

## check earliest and latest dates
print("""

Earliest and latest event dates in the dataset
""")
print(df[['SGSS_pve_test_date', 'PC_pve_test_date', 'PC_case_date', 'death_date']].agg(['min', 'max']).transpose())



# -


# ## Total number of deaths following a positive swab 
# From 1 Feb 2020 until 1 July 2020. As recorded in OpenSAFELY, and will exclude cases and deaths reported late

# +

## check death frequency
print("""

number of deaths following positive swab (recorded in SGSS)
""")
print(df_pvetestSGSS['death_category'].value_counts())

print("""

number of deaths following positive swab (recorded in primary care)
""")
print(df_pvetestPC['death_category'].value_counts())


print("""

number of deaths following covid case identification (recorded in primary care)
""")
print(df_casePC['death_category'].value_counts())


# -

## function that takes event times and a censor indicator (1=event, 0=censor)
## and produces a kaplan meier estimates in a dataframe
def KMestimate(times, indicators):   

    times = np.array(times)
    indicators = np.array(indicators)
    sortinds = times.argsort()
    times = times[sortinds]
    indicators = indicators[sortinds]

    min_time = 0
    max_time = times.max()
    atrisk0 = len(times)

    unq_times, counts = np.unique(times, return_counts=True)
    event_times, event_counts = np.unique(times[indicators==1], return_counts=True)
    censor_times, censor_counts = np.unique(times[indicators==0], return_counts=True)
    
    cml_counts = counts.cumsum()
    atrisk = (atrisk0-cml_counts) + counts

    kmdata = pd.DataFrame({
        'times': unq_times, 
        'atrisk': atrisk
    }).merge(
        pd.DataFrame({
            'times': event_times, 
            'died': event_counts
        }), on="times", how='left'
    ).merge(
        pd.DataFrame({
            'times': censor_times, 
            'censored': censor_counts
        }), on="times", how='left'
    )

    kmdata[['died','censored']] = kmdata[['died','censored']].fillna(0)
    
    
    kmdata['kmestimate'] = 1
    for i in kmdata.index:
        if i==0:
            kmdata.loc[i, 'kmestimate'] = 1 * (kmdata.loc[i, 'atrisk'] - kmdata.loc[i, 'died'])/kmdata.loc[i, 'atrisk']
        else:
            kmdata.loc[i, 'kmestimate'] = kmdata.loc[i-1, 'kmestimate'] * (kmdata.loc[i, 'atrisk'] - kmdata.loc[i, 'died'])/kmdata.loc[i, 'atrisk']

    return kmdata

# ## Deaths following a positive covid swab (SGSS)
#
# ### Survival curves

# +

fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(10,5), sharey=True)

# excluding non SGSS positive tests

kmdata = KMestimate(df_pvetestSGSS['pvetestSGSS_to_death'], df_pvetestSGSS['indicator_death'])
kmdata_covid = KMestimate(df_pvetestSGSS['pvetestSGSS_to_death'], df_pvetestSGSS['indicator_death_anycovid'])
kmdata_noncovid = KMestimate(df_pvetestSGSS['pvetestSGSS_to_death'], df_pvetestSGSS['indicator_death_notanycovid'])

axes[0].step(kmdata['times'], 1-kmdata['kmestimate'], label='all deaths') 
axes[0].step(kmdata_covid['times'], 1-kmdata_covid['kmestimate'], label='covid deaths') 
axes[0].step(kmdata_noncovid['times'], 1-kmdata_noncovid['kmestimate'], label = 'non-covid deaths')
axes[0].set_xlabel('time from positive test (from SGSS) to death')
axes[0].set_ylabel('1 - KM survival estimate')
axes[0].set_title("Including tests appearing 'after' death")
axes[0].legend()
axes[0].set_xlim(0, 90)
#plt.show()


# excluding non SGSS positive tests and negative time to death
df_pvetestSGSSfrom0 = df_pvetestSGSS.copy()[(df_pvetestSGSS['pvetestSGSS_to_death']>=0)]
kmdata = KMestimate(df_pvetestSGSSfrom0['pvetestSGSS_to_death'], df_pvetestSGSSfrom0['indicator_death'])
kmdata_covid = KMestimate(df_pvetestSGSSfrom0['pvetestSGSS_to_death'], df_pvetestSGSSfrom0['indicator_death_anycovid'])
kmdata_noncovid = KMestimate(df_pvetestSGSSfrom0['pvetestSGSS_to_death'], df_pvetestSGSSfrom0['indicator_death_notanycovid'])

axes[1].step(kmdata['times'], 1-kmdata['kmestimate'], label='all deaths') 
axes[1].step(kmdata_covid['times'], 1-kmdata_covid['kmestimate'], label='covid deaths') 
axes[1].step(kmdata_noncovid['times'], 1-kmdata_noncovid['kmestimate'], label = 'non-covid deaths')
axes[1].set_xlabel('time from positive test (from SGSS) to death')
axes[1].set_ylabel('1 - KM survival estimate')
axes[1].set_title("Excluding tests appearing 'after' death")
axes[1].set_xlim(0, 90)
#plt.show()

fig.tight_layout()
#kmdata


# -

# ### Underlying causes of death codes (ICD-10) amongst non-covid deaths
# codes occurring less than 10 times are included in the "_other_" category.

# +
df_pvetestSGSSnoncoviddeath = df_pvetestSGSS.copy()[~np.isnan(df_pvetestSGSS['pvetestSGSS_to_death']) & (df_pvetestSGSS['death_category']=="non-covid-death")]

cods = pd.value_counts(df_pvetestSGSSnoncoviddeath.death_underlyingcause)
mask = cods.lt(10)
#cods[~mask]
df_pvetestSGSSnoncoviddeath['death_underlyingcause'] = np.where(df_pvetestSGSSnoncoviddeath['death_underlyingcause'].isin(cods[mask].index), "_Other_", df_pvetestSGSSnoncoviddeath['death_underlyingcause'])
print(df_pvetestSGSSnoncoviddeath['death_underlyingcause'].value_counts().to_string())

# -

# ## Death following positive covid swab (primary care)
# ### Survival curves

# +

fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(10,5), sharey=True)

# excluding non PC positive tests
kmdata = KMestimate(df_pvetestPC['pvetestPC_to_death'], df_pvetestPC['indicator_death'])
kmdata_covid = KMestimate(df_pvetestPC['pvetestPC_to_death'], df_pvetestPC['indicator_death_anycovid'])
kmdata_noncovid = KMestimate(df_pvetestPC['pvetestPC_to_death'], df_pvetestPC['indicator_death_notanycovid'])

axes[0].step(kmdata['times'], 1-kmdata['kmestimate'], label='all deaths') 
axes[0].step(kmdata_covid['times'], 1-kmdata_covid['kmestimate'], label='covid deaths') 
axes[0].step(kmdata_noncovid['times'], 1-kmdata_noncovid['kmestimate'], label = 'non-covid deaths')
axes[0].set_xlabel('time from positive test (from primary care) to death')
axes[0].set_ylabel('1 - KM survival estimate')
axes[0].set_title("Including tests appearing 'after' death")
axes[0].legend()
axes[0].set_xlim(0, 90)



# excluding non PC positive tests and negative time to death
df_pvetestPCfrom0 = df_pvetestPC.copy()[(df_pvetestPC['pvetestPC_to_death']>=0)]
kmdata = KMestimate(df_pvetestPCfrom0['pvetestPC_to_death'], df_pvetestPCfrom0['indicator_death'])
kmdata_covid = KMestimate(df_pvetestPCfrom0['pvetestPC_to_death'], df_pvetestPCfrom0['indicator_death_anycovid'])
kmdata_noncovid = KMestimate(df_pvetestPCfrom0['pvetestPC_to_death'], df_pvetestPCfrom0['indicator_death_notanycovid'])

axes[1].step(kmdata['times'], 1-kmdata['kmestimate'], label='all deaths') 
axes[1].step(kmdata_covid['times'], 1-kmdata_covid['kmestimate'], label='covid deaths') 
axes[1].step(kmdata_noncovid['times'], 1-kmdata_noncovid['kmestimate'], label = 'non-covid deaths')
axes[1].set_xlabel('time from positive test (from primary care) to death')
axes[1].set_ylabel('1 - KM survival estimate')
axes[1].set_title("Excluding tests appearing 'after' death")
axes[1].set_xlim(0, 90)

fig.tight_layout()


# -
# ### Underlying cause of death codes (ICD-10) amongst non-covid deaths
# codes occurring less than 10 times are included in the "_other_" category.

# +
df_pvetestPCnoncoviddeath = df_pvetestPC.copy()[~np.isnan(df_pvetestPC['pvetestPC_to_death']) & (df_pvetestPC['death_category']=="non-covid-death")]

cods = pd.value_counts(df_pvetestPCnoncoviddeath.death_underlyingcause)
mask = cods.lt(10)
#cods[~mask]
df_pvetestPCnoncoviddeath['death_underlyingcause'] = np.where(df_pvetestPCnoncoviddeath['death_underlyingcause'].isin(cods[mask].index), "_Other_", df_pvetestPCnoncoviddeath['death_underlyingcause'])
print(df_pvetestPCnoncoviddeath['death_underlyingcause'].value_counts().to_string())

# -


# ## Death following COVID case identification (primary care)
# ### Survival curves

# +

fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(10,5), sharey=True)

# excluding non PC positive tests
kmdata = KMestimate(df_casePC['casePC_to_death'], df_casePC['indicator_death'])
kmdata_covid = KMestimate(df_casePC['casePC_to_death'], df_casePC['indicator_death_anycovid'])
kmdata_noncovid = KMestimate(df_casePC['casePC_to_death'], df_casePC['indicator_death_notanycovid'])

axes[0].step(kmdata['times'], 1-kmdata['kmestimate'], label='all deaths') 
axes[0].step(kmdata_covid['times'], 1-kmdata_covid['kmestimate'], label='covid deaths') 
axes[0].step(kmdata_noncovid['times'], 1-kmdata_noncovid['kmestimate'], label = 'non-covid deaths')
axes[0].set_xlabel('time from case identification (from primary care) to death')
axes[0].set_ylabel('1 - KM survival estimate')
axes[0].set_title("Including tests appearing 'after' death")
axes[0].legend()
axes[0].set_xlim(0, 90)



# excluding non PC positive tests and negative time to death
df_casePCfrom0 = df_casePC.copy()[(df_casePC['casePC_to_death']>=0)]
kmdata = KMestimate(df_casePCfrom0['casePC_to_death'], df_casePCfrom0['indicator_death'])
kmdata_covid = KMestimate(df_casePCfrom0['casePC_to_death'], df_casePCfrom0['indicator_death_anycovid'])
kmdata_noncovid = KMestimate(df_casePCfrom0['casePC_to_death'], df_casePCfrom0['indicator_death_notanycovid'])

axes[1].step(kmdata['times'], 1-kmdata['kmestimate'], label='all deaths') 
axes[1].step(kmdata_covid['times'], 1-kmdata_covid['kmestimate'], label='covid deaths') 
axes[1].step(kmdata_noncovid['times'], 1-kmdata_noncovid['kmestimate'], label = 'non-covid deaths')
axes[1].set_xlabel('time from case identification (from primary care) to death')
axes[1].set_ylabel('1 - KM survival estimate')
axes[1].set_title("Excluding tests appearing 'after' death")
axes[1].set_xlim(0, 90)

fig.tight_layout()


# -
# ### Underlying cause of death codes (ICD-10) amongst non-covid deaths
# codes occurring less than 10 times are included in the "_other_" category.

# +
df_casePCnoncoviddeath = df_casePC.copy()[~np.isnan(df_casePC['casePC_to_death']) & (df_casePC['death_category']=="non-covid-death")]

cods = pd.value_counts(df_casePCnoncoviddeath.death_underlyingcause)
mask = cods.lt(10)
#cods[~mask]
df_casePCnoncoviddeath['death_underlyingcause'] = np.where(df_casePCnoncoviddeath['death_underlyingcause'].isin(cods[mask].index), "_Other_", df_casePCnoncoviddeath['death_underlyingcause'])
print(df_casePCnoncoviddeath['death_underlyingcause'].value_counts().to_string())

# -




# ### Notes on OpenSAFELY
#
# OpenSAFELY is a data analytics platform built by a mixed team of software developers, clinicians, and epidemiologists from the Oxford DataLab, London School of Hygiene and Tropical Medicine Electronic Health Record research group, health software company TPP and NHS England. It represents a fundamentally different way of conducting electronic health record (EHR) research: instead of sending EHR data to a third party for analysis, we've developed a system for conducting analyses within the secure environment where the data is already stored, so that the electronic health record data never leaves the NHS ecosystem.
#
# Currently, OpenSAFELY uses the electronic health records of all patients registered at a GP practice using the SystmOne clinical information system run by TPP, covering around 22 million people. Additional data for these patients covering COVID-related tests, hospital admissions, ITU admissions, and registered deaths are also securely imported to the platform.
#
# For more information, visit https://opensafely.org


