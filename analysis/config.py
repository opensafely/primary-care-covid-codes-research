import pandas as pd

# state start / end dates
start_date = pd.to_datetime("2020-11-14", format='%Y-%m-%d')
end_date = pd.to_datetime("2021-11-14", format='%Y-%m-%d')
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

