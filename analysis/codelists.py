from cohortextractor import codelist, codelist_from_csv

codes_antigen_negative = codelist_from_csv(
    "codelists/opensafely-covid-identification-in-primary-care-antigen-test-negative.csv",
    system="ctv3",
    column="CTV3ID",
)

codes_exposure_to_disease = codelist_from_csv(
    "codelists/opensafely-covid-identification-in-primary-care-exposure-to-disease.csv",
    system="ctv3",
    column="CTV3ID",
)

codes_historic_covid = codelist_from_csv(
    "codelists/opensafely-covid-identification-in-primary-care-historic-case.csv",
    system="ctv3",
    column="CTV3ID",
)

codes_potential_historic_covid = codelist_from_csv(
    "codelists/opensafely-covid-identification-in-primary-care-potential-historic-case.csv",
    system="ctv3",
    column="CTV3ID",
)

codes_probable_covid = codelist_from_csv(
    "codelists/opensafely-covid-identification-in-primary-care-probable-covid-clinical-code.csv",
    system="ctv3",
    column="CTV3ID",
)


codes_probable_covid_pos_test = codelist_from_csv(
    "codelists/opensafely-covid-identification-in-primary-care-probable-covid-positive-test.csv",
    system="ctv3",
    column="CTV3ID",
)

codes_probable_covid_sequelae = codelist_from_csv(
    "codelists/opensafely-covid-identification-in-primary-care-probable-covid-sequelae.csv",
    system="ctv3",
    column="CTV3ID",
)


codes_suspected_covid_advice = codelist_from_csv(
    "codelists/opensafely-covid-identification-in-primary-care-suspected-covid-advice.csv",
    system="ctv3",
    column="CTV3ID",
)


codes_suspected_covid_had_test = codelist_from_csv(
    "codelists/opensafely-covid-identification-in-primary-care-suspected-covid-had-test.csv",
    system="ctv3",
    column="CTV3ID",
)

codes_suspected_covid_isolation = codelist_from_csv(
    "codelists/opensafely-covid-identification-in-primary-care-suspected-covid-isolation-code.csv",
    system="ctv3",
    column="CTV3ID",
)


codes_suspected_covid_nonspecific = codelist_from_csv(
    "codelists/opensafely-covid-identification-in-primary-care-suspected-covid-nonspecific-clinical-assessment.csv",
    system="ctv3",
    column="CTV3ID",
)


codes_suspected_covid = codelist_from_csv(
    "codelists/opensafely-covid-identification-in-primary-care-suspected-covid-suspected-codes.csv",
    system="ctv3",
    column="CTV3ID",
)


codes_covid_unrelated_to_case_status = codelist_from_csv(
    "codelists/opensafely-covid-identification-in-primary-care-unrelated-to-case-status.csv",
    system="ctv3",
    column="CTV3ID",
)

codes_suspected_covid_had_antigen_test = codelist_from_csv(
    "codelists/user-candrews-covid-identification-in-primary-care-suspected-covid-had-antigen-test.csv",
    system="ctv3",
    column="code",
)

covid_icd10 = codelist_from_csv(
    "codelists/opensafely-covid-identification.csv", system="icd10", column="icd10_code"
)

codes_covid_caseness = codelist_from_csv(
    "codelists/user-candrews-covid_caseness.csv", system="ctv3", column="code"
)