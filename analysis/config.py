import pandas as pd

# state start / end dates
start_date = pd.to_datetime("2020-02-01", format="%Y-%m-%d")
end_date = pd.to_datetime("2021-11-28", format="%Y-%m-%d")

# set minimum no of days between two events
min_days = 21

# set maximum number of events per patient
n = 6
