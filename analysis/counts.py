import sys
import os
import pandas as pd

from config import end_date, m, n, start_date

sys.path.append("lib/")
from functions import *

os.makedirs("output/caseness")
# import data
df = pd.read_feather("output/input.feather")

# Make a dataframe with consecutive dates
consec_dates = pd.DataFrame(
    index=pd.date_range(start=start_date, end=end_date, freq="D")
)

# choose only date variables
activity_dates = df[[col for col in df.columns if col.endswith("_date")]]
activity_dates.columns = activity_dates.columns.str.replace("_date", "X")

# count code activity per day
codecounts_day = activity_dates.apply(
    lambda x: eventcountseries(event_dates=x, date_range=consec_dates)
)

# select the codelists with multiple events
codelists_n = [
    "exposure_to_disease",
    "historic_covid",
    "probable_covid_sequelae",
    "probable_covid_pos_test",
    "suspected_covid_isolation",
    "suspected_covid_nonspecific",
    "suspected_covid_had_antigen_test",
    "sgss_positive_test",
    "covid_caseness"
]


codelists_m = [
    "antigen_negative",
    "potential_historic_covid",
    "suspected_covid_advice",
    "suspected_covid_had_test",
    "covid_unrelated_to_case_status",
    "suspected_covid",
    "probable_covid",
]
codelists = codelists_n + codelists_m

# collapse multiple events into one for each codelist
for list in codelists:
    codecounts_day[list] = codecounts_day[
        [col for col in codecounts_day.columns if col.startswith(f"{list}_X")]
    ].sum(axis=1)

codecounts_day.columns = codecounts_day.columns.str.strip("_X")
codecounts_day = codecounts_day.filter(items=codelists)

# derive count activity per week
codecounts_week = codecounts_day.resample("W").sum()

# small number redaction
# cols = codecounts_week.columns.values.tolist()
# for col in codelists:
#     codecounts_week = redact_small_numbers_minimal(codecounts_week, col)

def redact_round_table(df_in):
    """Redacts counts <= 5 and rounds counts to nearest 5"""
    df_in = df_in.where(df_in > 5, np.nan).apply(lambda x: 5 * round(x / 5))
    return df_in

codecounts_week=redact_round_table(codecounts_week)

codecounts_week.to_csv("output/caseness/codecounts_week.csv")
