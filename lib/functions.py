import pandas as pd
import numpy as np


 
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

def redact_small_numbers(df, n, colname):
    def suppress_column(column):
        suppressed_count = column[column <= n].sum()
        if suppressed_count == 0:
            pass
        
        else:
            column[column <= n] = np.nan
            
            while suppressed_count <= n:
                suppressed_count += column.min()
                column[column.idxmin()] = np.nan
        
        return column
                
    df_list = []
    df[colname] = suppress_column(df[colname])
    df_list.append(df)
    return pd.concat(df_list, axis=0) 
