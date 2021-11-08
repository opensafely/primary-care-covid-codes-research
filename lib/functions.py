import pandas as pd
import numpy as np
# import pyodbc
import os
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from contextlib import contextmanager



# use this to open connection
# @contextmanager
# def closing_connection(dbconn): 
#     cnxn = pyodbc.connect(dbconn)
#     try: 
#         yield cnxn 
#     finally: 
#         cnxn.close()


def DBbuildtimes(cnxn, up_to=None):

    # returns a dataframe containing the latest build time for the OS DB tables
    # if up_to is specified, it takes the most recent build before that date
    
    if up_to is None:
        up_to = pd.to_datetime('today')
    else:
        assert (type(up_to) is pd.Timestamp),  "up_to must be a Timestamp, eg using `pd.to_datetime()`"
    
    tablebuild = pd.read_sql(f"""
        select b.BuildDesc as dataset, max(b.BuildDate) as latest_build from BuildInfo as b cross join LatestBuildTime as l
        where b.BuildDate <= l.DtLatestBuild and b.BuildDate <= convert(date, '{up_to.strftime('%Y-%m-%d %H:%M:%S')}')
        group by b.BuildDesc
    """, cnxn)

    return(tablebuild)

   
    
def eventcountdf(event_dates, date_range, rule='D', popadjust=False):
    # to calculate the daily count for events recorded in a dataframe
    # where event_dates is a dataframe of date columns
    # set popadjust = 1000, say, to report counts per 1000 population
    
    # initialise dataset
    counts = date_range
    
    
    for col in event_dates:

        # Creates a series of the entry date of the index event
        in_date = event_dates.loc[:, col]

        counts = counts.join(
            pd.DataFrame(in_date, columns=[col]).groupby(col)[col].count().to_frame()
        )

    # convert nan to zero
    counts = counts.fillna(0)
    
    if rule != "D":
        counts = counts.resample(rule).sum()
    
    if popadjust is not False:
        pop = event_dates.shape[0]
        poppern = pop/popadjust
        counts = counts.transform(lambda x: x/poppern)
    
    return(counts)

    


def eventcountseries(event_dates, date_range, rule='D', popadjust=False):
    # to calculate the daily count for events recorded in a series
    # where event_dates is a series
    # set popadjust = 1000, say, to report counts per 1000 population
    
    pop = event_dates.size
    
    counts = event_dates.value_counts().reindex(date_range.index, fill_value=0)
    
    
    if rule != "D":
        counts = counts.resample(rule).sum()
    
    if popadjust is not False:
        pop = event_dates.size
        poppern= pop/popadjust
        counts = counts.transform(lambda x: x/poppern)
    
    return(counts)



def KMestimate(times, indicators):   

    ## function that takes event times (=times, a series) and a censor indicator (=indicators, a series taking values 1=event, 0=censor)
    ## and produces a kaplan meier estimates in a dataframe

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