import os
import pandas as pd
# import matplotlib.ticker as ticker
from contextlib import contextmanager
# from datetime import date , timedelta
from config import start_date, end_date, today


import sys
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

#when was the study cohort csv file last updated?
cohort_run_date = pd.to_datetime(os.path.getmtime("output/input.csv"), unit='s')

# # get build times from the database
# with closing_connection(dbconn) as cnxn:
#     DBbuild = pd.read_sql("""select * from LatestBuildTime""", cnxn)
#     tablebuild = pd.read_sql(f"""
#        select 
#            max(BuildDate) as builddate from BuildInfo
#        where 
#            BuildDesc = 'S1' and 
#            BuildDate <= convert(date, '{cohort_run_date.strftime('%Y-%m-%d %H:%M:%S')}')
#     """, cnxn)

# DB_build_date = pd.to_datetime(DBbuild['DtLatestBuild'].values[0], format='%Y-%m-%d')
# S1_build_date = pd.to_datetime(tablebuild['builddate'].values[0], format='%Y-%m-%d')


# Make a dataframe with consecutive dates
consec_dates = pd.DataFrame(
    index=pd.date_range(start=start_date, end=end_date, freq="D")
)

# choose only date variables
activity_dates = df.filter(items=date_cols)
activity_dates.columns = activity_dates.columns.str.replace("date_", "")

# count code activity per day
codecounts_day = activity_dates.apply(lambda x: eventcountseries(event_dates=x, date_range = consec_dates))

#derive count activity per week
codecounts_week = codecounts_day.resample('W').sum()
codecounts_week.to_csv("output/codecounts_week.csv")

#derive total code activity over whole time period
codecounts_total = codecounts_week.sum()

tableindex = [
    "probable_covid",
    "probable_covid_pos_test",
    "probable_covid_sequelae",
    "suspected_covid_advice",
    "suspected_covid_had_test",
    "suspected_covid_isolation",
    "suspected_covid_nonspecific",
    "suspected_covid",
    "historic_covid",
    "potential_historic_covid",
    "exposure_to_disease",
    "antigen_negative",
    "covid_unrelated_to_case_status"
]

tabledata = {
    'Category':[
        'Probable case',
        '',
        '',
        'Suspected case',
        '',
        '',
        '',
        '',
        'Historic case',
        'Potential historic case',
        'Exposure to disease',
        'Antigen test negative',
        'COVID-19 related but case status not specified',        
    ],
    'Sub-category':[
        'Clinical code',
        'Positive test',
        'Sequalae',
        'Advice',
        'Had test',
        'Isolation code',
        'Non-specific clinical assessment',
        'Suspected codes',
        '-',
        '-',
        '-',
        '-',
        '-',
    ],
    'Codelist':[
        'Probable case: clinical code',
        'Probable case: positive test',
        'Probable case: sequelae',
        'Suspected case: advice',
        'Suspected case: had test',
        'Suspected case: isolation code',
        'Suspected case: non-specific clinical assessment',
        'Suspected case: suspected codes',
        'Historic case',
        'Potential historic case',
        'Exposure to disease',
        'Antigen test negative',
        'COVID-19 related but case status not specified',   
    ],
    'Description':[
        'Clinical diagnosis of COVID-19 made',
        'Record of positive test result for SARS-CoV-2 (active infection)',
        'Symptom or condition recorded as secondary to SARS-CoV-2',
        'General advice given about SARS-CoV-2',
        'Record of having had a test for active infection with SARS-CoV-2',
        'Self- or household-isolation recorded',
        'Clinical assessments plausibly related to COVID-19',
        '"Suspect" mentioned, or previous COVID-19 reported',
        'SARS-CoV-2 antibodies or immunity recorded',
        'Has had a test for SARS-CoV-2 antibodies',
        'Record of contact/exposure/procedure',
        'Record of negative test result for SARS-CoV-2',
        'Healthcare contact related to COVID-19 but not case status',      
    ],
    'link':[
        "https://codelists.opensafely.org/codelist/opensafely/covid-identification-in-primary-care-probable-covid-clinical-code/2020-07-16/",
        "https://codelists.opensafely.org/codelist/opensafely/covid-identification-in-primary-care-probable-covid-positive-test/2020-07-16/",
        "https://codelists.opensafely.org/codelist/opensafely/covid-identification-in-primary-care-probable-covid-sequelae/2020-07-16/",
        "https://codelists.opensafely.org/codelist/opensafely/covid-identification-in-primary-care-suspected-covid-advice/2020-07-16/",
        "https://codelists.opensafely.org/codelist/opensafely/covid-identification-in-primary-care-suspected-covid-had-test/2020-07-16/",
        "https://codelists.opensafely.org/codelist/opensafely/covid-identification-in-primary-care-suspected-covid-isolation-code/2020-07-16/",
        "https://codelists.opensafely.org/codelist/opensafely/covid-identification-in-primary-care-suspected-covid-nonspecific-clinical-assessment/2020-07-16/",
        "https://codelists.opensafely.org/codelist/opensafely/covid-identification-in-primary-care-suspected-codes-suspected-codes/2020-07-16/",
        "https://codelists.opensafely.org/codelist/opensafely/covid-identification-in-primary-care-historic-case/2020-06-23/",
        "https://codelists.opensafely.org/codelist/opensafely/covid-identification-in-primary-care-potential-historic-case/2020-06-23/",
        "https://codelists.opensafely.org/codelist/opensafely/covid-identification-in-primary-care-exposure-to-disease/2020-06-23/",
        "https://codelists.opensafely.org/codelist/opensafely/covid-identification-in-primary-care-antigen-test-negative/2020-06-24/",
        "https://codelists.opensafely.org/codelist/opensafely/covid-identification-in-primary-care-unrelated-to-case-status/2020-06-23/",
    ]
}

tabledata = pd.DataFrame(tabledata, index=tableindex)
tabledata['Codelist']="<a href='"+tabledata['link']+"' target='_blank'>"+tabledata['Codelist']+"</a>"

codecounts_total.name = "Count"

tabledata = tabledata.merge(codecounts_total, left_index=True, right_index=True)

# easy but not ideal output
#display(HTML(tabledata.to_html(index=False, justify='left')))

# use styling instead - https://pandas.pydata.org/pandas-docs/stable/user_guide/style.html
styles = [dict(selector="th", props=[("text-align", "left")])]

# with hyperlinks
tabledata[["Codelist", "Description", "Count"]].style.set_properties(subset=["Codelist","Description"], **{'text-align':'left', 'index':False}).set_table_styles(styles).hide_index()

#without hyperlinks
#tabledata[["Category", "Sub-category" "Description", "Count"]].style.set_properties(subset=["Category","Sub-category","Description"], **{'text-align':'left', 'index':False}).set_table_styles(styles).hide_index()
tabledata.to_csv("output/tabledata.csv")



