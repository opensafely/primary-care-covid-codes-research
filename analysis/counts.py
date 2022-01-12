import pandas as pd
from config import start_date, end_date, date_cols
import sys
sys.path.append('lib/')
from functions import *

def redact_small_numbers(df, column):
    mask = df[column].isin([1, 2, 3, 4, 5])
    df.loc[mask, column] = 0
    return df

# import data
df = pd.read_csv(
    filepath_or_buffer = 'output/input.csv',    
    parse_dates = date_cols
)

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


#derive total code activity over whole time period
codecounts_total = codecounts_week.sum()

tableindex = [
    "probable_covid",
    "probable_covid_pos_test",
    "probable_covid_sequelae",
    "suspected_covid_advice",
    "suspected_covid_had_test",
    "suspected_covid_had_antigen_test",
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
        'Had antigen test',
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
        'Suspected case: had antigen test',
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
        'Record of having had an antigen test for infection with SARS-CoV-2',
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
        "https://codelists.opensafely.org/codelist/opensafely/covid-identification-in-primary-care-probable-covid-positive-test/0934bb24/",
        "https://codelists.opensafely.org/codelist/opensafely/covid-identification-in-primary-care-probable-covid-sequelae/2020-07-16/",
        "https://codelists.opensafely.org/codelist/opensafely/covid-identification-in-primary-care-suspected-covid-advice/2020-07-16/",
        "https://codelists.opensafely.org/codelist/opensafely/covid-identification-in-primary-care-suspected-covid-had-test/40b9217a/",
        "https://codelists.opensafely.org/codelist/user/candrews/covid-identification-in-primary-care-suspected-covid-had-antigen-test/0e9a3b10/",
        "https://codelists.opensafely.org/codelist/opensafely/covid-identification-in-primary-care-suspected-covid-isolation-code/2020-07-16/",
        "https://codelists.opensafely.org/codelist/opensafely/covid-identification-in-primary-care-suspected-covid-nonspecific-clinical-assessment/2020-07-16/",
        "https://codelists.opensafely.org/codelist/opensafely/covid-identification-in-primary-care-suspected-covid-suspected-codes/2020-07-16/",
        "https://codelists.opensafely.org/codelist/opensafely/covid-identification-in-primary-care-historic-case/2020-06-23/",
        "https://codelists.opensafely.org/codelist/opensafely/covid-identification-in-primary-care-potential-historic-case/0be77b1a/",
        "https://codelists.opensafely.org/codelist/opensafely/covid-identification-in-primary-care-exposure-to-disease/2020-06-23/",
        "https://codelists.opensafely.org/codelist/opensafely/covid-identification-in-primary-care-antigen-test-negative/702547ee/",
        "https://codelists.opensafely.org/codelist/opensafely/covid-identification-in-primary-care-unrelated-to-case-status/2020-06-23/",
    ]
}

tabledata = pd.DataFrame(tabledata, index=tableindex)
tabledata['Codelist']="<a href='"+tabledata['link']+"' target='_blank'>"+tabledata['Codelist']+"</a>"

codecounts_total.name = "Count"

tabledata = tabledata.merge(codecounts_total, left_index=True, right_index=True)
redact_small_numbers(tabledata,"Count").to_csv("output/tabledata.csv")

cols= codecounts_week.columns.values.tolist()
for col in cols:
    codecounts_week=redact_small_numbers(codecounts_week,col)

codecounts_week.to_csv("output/codecounts_week.csv")
