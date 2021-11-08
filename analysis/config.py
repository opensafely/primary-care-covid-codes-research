import pandas as pd
from datetime import date

# state start / end dates
start_date = pd.to_datetime("2020-02-01", format='%Y-%m-%d')
end_date = pd.to_datetime("2021-02-01", format='%Y-%m-%d') # a week last sunday
today = date.today()
