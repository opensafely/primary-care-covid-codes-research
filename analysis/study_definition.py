from cohortextractor import (
    StudyDefinition,
    patients,
    codelist_from_csv,
    codelist,
    filter_codes_by_category,
)

## CODE LISTS
# All codelist are held within the codelist/ folder.
from codelists import *


## STUDY POPULATION
# Defines both the study population and points to the important covariates


from_date = "2020-02-01"

study = StudyDefinition(
    default_expectations={
        "date": {"earliest": "1970-01-01", "latest": "today"},
        "rate": "uniform",
        "incidence": 0.2,
    },
    # This line defines the study population
    population=patients.registered_with_one_practice_between(
        "2019-02-01", "2020-02-01"
    ),

    
    
    # demographic info 
    # https://github.com/ebmdatalab/tpp-sql-notebook/issues/33
    age=patients.age_as_of(
        "2020-02-01",
        return_expectations={
            "rate": "universal",
            "int": {"distribution": "population_ages"},
        },
    ),
    # https://github.com/ebmdatalab/tpp-sql-notebook/issues/46
    sex=patients.sex(
        return_expectations={
            "rate": "universal",
            "category": {"ratios": {"M": 0.49, "F": 0.51}},
        }
    ),
    # https://github.com/ebmdatalab/tpp-sql-notebook/issues/52
    imd=patients.address_as_of(
        "2020-02-01",
        returning="index_of_multiple_deprivation",
        round_to_nearest=100,
        return_expectations={
            "rate": "universal",
            "category": {"ratios": {"100": 0.1, "200": 0.2, "300": 0.7}},
        },
    ),
    # https://github.com/ebmdatalab/tpp-sql-notebook/issues/54
    stp=patients.registered_practice_as_of(
        "2020-02-01",
        returning="stp_code",
        return_expectations={
            "rate": "universal",
            "category": {
                "ratios": {
                    "STP1": 0.1,
                    "STP2": 0.1,
                    "STP3": 0.1,
                    "STP4": 0.1,
                    "STP5": 0.1,
                    "STP6": 0.1,
                    "STP7": 0.1,
                    "STP8": 0.1,
                    "STP9": 0.1,
                    "STP10": 0.1,
                }
            },
        },
    ),
    # region - one of NHS England 9 regions
    region=patients.registered_practice_as_of(
        "2020-02-01",
        returning="nuts1_region_name",
        return_expectations={
            "rate": "universal",
            "category": {
                "ratios": {
                    "North East": 0.1,
                    "North West": 0.1,
                    "Yorkshire and the Humber": 0.1,
                    "East Midlands": 0.1,
                    "West Midlands": 0.1,
                    "East of England": 0.1,
                    "London": 0.2,
                    "South East": 0.2,
                },
            },
        },
    ),
    
       
    
    
    # covid-related codelists


    # cat_antigen_negative = patients.with_these_clinical_events(
    #     codes_antigen_negative,
    #     returning="category",
    #     on_or_after=from_date,
    #     #find_first_match_in_period=True,
    #     #date_format="YYYY-MM-DD",
    #     return_expectations={
    #         #"date": {"earliest": "2020-03-01"},
    #         "category": {"ratios": {"Y20ce": 0.5, "Y229e": 0.5}},
    #     },
    # ),
    #
    # cat_exposure_to_disease=patients.with_these_clinical_events(
    #     codes_exposure_to_disease,
    #     returning="category",
    #     on_or_after=from_date,
    #     #find_first_match_in_period=True,
    #     #date_format="YYYY-MM-DD",
    #     return_expectations={
    #         #"date": {"earliest": "2020-03-01"},
    #         "category": {"ratios": {"Y20ce": 0.5, "Y229e": 0.5}},
    #     },
    # ),
    #
    # cat_historic_covid=patients.with_these_clinical_events(
    #     codes_historic_covid,
    #     returning="category",
    #     on_or_after=from_date,
    #     # find_first_match_in_period=True,
    #     # date_format="YYYY-MM-DD",
    #     return_expectations={
    #         # "date": {"earliest": "2020-03-01"},
    #         "category": {"ratios": {"Y20ce": 0.5, "Y229e": 0.5}},
    #     },
    # ),
    #
    # cat_potential_historic_covid=patients.with_these_clinical_events(
    #     codes_potential_historic_covid,
    #     returning="category",
    #     on_or_after=from_date,
    #     # find_first_match_in_period=True,
    #     # date_format="YYYY-MM-DD",
    #     return_expectations={
    #         # "date": {"earliest": "2020-03-01"},
    #         "category": {"ratios": {"Y20ce": 0.5, "Y229e": 0.5}},
    #     },
    # ),
    #
    # cat_probable_covid=patients.with_these_clinical_events(
    #     codes_probable_covid,
    #     returning="category",
    #     on_or_after=from_date,
    #     # find_first_match_in_period=True,
    #     # date_format="YYYY-MM-DD",
    #     return_expectations={
    #         # "date": {"earliest": "2020-03-01"},
    #         "category": {"ratios": {"Y20ce": 0.5, "Y229e": 0.5}},
    #     },
    # ),
    #
    # cat_probable_covid_pos_test=patients.with_these_clinical_events(
    #     codes_probable_covid_pos_test,
    #     returning="category",
    #     on_or_after=from_date,
    #     # find_first_match_in_period=True,
    #     # date_format="YYYY-MM-DD",
    #     return_expectations={
    #         # "date": {"earliest": "2020-03-01"},
    #         "category": {"ratios": {"Y20ce": 0.5, "Y229e": 0.5}},
    #     },
    # ),
    #
    # cat_probable_covid_sequelae=patients.with_these_clinical_events(
    #     codes_probable_covid_sequelae,
    #     returning="category",
    #     on_or_after=from_date,
    #     # find_first_match_in_period=True,
    #     # date_format="YYYY-MM-DD",
    #     return_expectations={
    #         # "date": {"earliest": "2020-03-01"},
    #         "category": {"ratios": {"Y20ce": 0.5, "Y229e": 0.5}},
    #     },
    # ),
    #
    # cat_suspected_covid_advice=patients.with_these_clinical_events(
    #     codes_suspected_covid_advice,
    #     returning="category",
    #     on_or_after=from_date,
    #     # find_first_match_in_period=True,
    #     # date_format="YYYY-MM-DD",
    #     return_expectations={
    #         # "date": {"earliest": "2020-03-01"},
    #         "category": {"ratios": {"Y20ce": 0.5, "Y229e": 0.5}},
    #     },
    # ),
    #
    # cat_suspected_covid_had_test=patients.with_these_clinical_events(
    #     codes_suspected_covid_had_test,
    #     returning="category",
    #     on_or_after=from_date,
    #     # find_first_match_in_period=True,
    #     # date_format="YYYY-MM-DD",
    #     return_expectations={
    #         # "date": {"earliest": "2020-03-01"},
    #         "category": {"ratios": {"Y20ce": 0.5, "Y229e": 0.5}},
    #     },
    # ),
    #
    # cat_suspected_covid_isolation=patients.with_these_clinical_events(
    #     codes_suspected_covid_isolation,
    #     returning="category",
    #     on_or_after=from_date,
    #     # find_first_match_in_period=True,
    #     # date_format="YYYY-MM-DD",
    #     return_expectations={
    #         # "date": {"earliest": "2020-03-01"},
    #         "category": {"ratios": {"Y20ce": 0.5, "Y229e": 0.5}},
    #     },
    # ),
    #
    # cat_suspected_covid_nonspecific=patients.with_these_clinical_events(
    #     codes_suspected_covid_nonspecific,
    #     returning="category",
    #     on_or_after=from_date,
    #     # find_first_match_in_period=True,
    #     # date_format="YYYY-MM-DD",
    #     return_expectations={
    #         # "date": {"earliest": "2020-03-01"},
    #         "category": {"ratios": {"Y20ce": 0.5, "Y229e": 0.5}},
    #     },
    # ),
    #
    # cat_suspected_covid=patients.with_these_clinical_events(
    #     codes_suspected_covid,
    #     returning="category",
    #     on_or_after=from_date,
    #     # find_first_match_in_period=True,
    #     # date_format="YYYY-MM-DD",
    #     return_expectations={
    #         # "date": {"earliest": "2020-03-01"},
    #         "category": {"ratios": {"Y20ce": 0.5, "Y229e": 0.5}},
    #     },
    # ),
    #
    # cat_covid_unrelated_to_case_status=patients.with_these_clinical_events(
    #     codes_covid_unrelated_to_case_status,
    #     returning="category",
    #     on_or_after=from_date,
    #     # find_first_match_in_period=True,
    #     # date_format="YYYY-MM-DD",
    #     return_expectations={
    #         # "date": {"earliest": "2020-03-01"},
    #         "category": {"ratios": {"Y20ce": 0.5, "Y229e": 0.5}},
    #     },
    # ),
    #



    # covid-related code dates

    date_antigen_negative=patients.with_these_clinical_events(
        codes_antigen_negative,
        returning="date",
        on_or_after=from_date,
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
        return_expectations={
            "date": {"earliest": "2020-03-01"},
        },
    ),

    date_exposure_to_disease=patients.with_these_clinical_events(
        codes_exposure_to_disease,
        returning="date",
        on_or_after=from_date,
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
        return_expectations={
            "date": {"earliest": "2020-03-01"},
        },
    ),

    date_historic_covid=patients.with_these_clinical_events(
        codes_historic_covid,
        returning="date",
        on_or_after=from_date,
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
        return_expectations={
            "date": {"earliest": "2020-03-01"},
        },
    ),

    date_potential_historic_covid=patients.with_these_clinical_events(
        codes_potential_historic_covid,
        returning="date",
        on_or_after=from_date,
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
        return_expectations={
            "date": {"earliest": "2020-03-01"},
        },
    ),

    date_probable_covid=patients.with_these_clinical_events(
        codes_probable_covid,
        returning="date",
        on_or_after=from_date,
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
        return_expectations={
            "date": {"earliest": "2020-03-01"},
        },
    ),

    date_probable_covid_pos_test=patients.with_these_clinical_events(
        codes_probable_covid_pos_test,
        returning="date",
        on_or_after=from_date,
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
        return_expectations={
            "date": {"earliest": "2020-03-01"},
        },
    ),

    date_probable_covid_sequelae=patients.with_these_clinical_events(
        codes_probable_covid_sequelae,
        returning="date",
        on_or_after=from_date,
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
        return_expectations={
            "date": {"earliest": "2020-03-01"},
        },
    ),

    date_suspected_covid_advice=patients.with_these_clinical_events(
        codes_suspected_covid_advice,
        returning="date",
        on_or_after=from_date,
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
        return_expectations={
            "date": {"earliest": "2020-03-01"},
        },
    ),

    date_suspected_covid_had_test=patients.with_these_clinical_events(
        codes_suspected_covid_had_test,
        returning="date",
        on_or_after=from_date,
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
        return_expectations={
            "date": {"earliest": "2020-03-01"},
        },
    ),

    date_suspected_covid_isolation=patients.with_these_clinical_events(
        codes_suspected_covid_isolation,
        returning="date",
        on_or_after=from_date,
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
        return_expectations={
            "date": {"earliest": "2020-03-01"},
        },
    ),

    date_suspected_covid_nonspecific=patients.with_these_clinical_events(
        codes_suspected_covid_nonspecific,
        returning="date",
        on_or_after=from_date,
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
        return_expectations={
            "date": {"earliest": "2020-03-01"},
        },
    ),

    date_suspected_covid=patients.with_these_clinical_events(
        codes_suspected_covid,
        returning="date",
        on_or_after=from_date,
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
        return_expectations={
            "date": {"earliest": "2020-03-01"},
        },
    ),

    date_covid_unrelated_to_case_status=patients.with_these_clinical_events(
        codes_covid_unrelated_to_case_status,
        returning="date",
        on_or_after=from_date,
        find_first_match_in_period=True,
        date_format="YYYY-MM-DD",
        return_expectations={
            "date": {"earliest": "2020-03-01"},
        },
    ),


    date_sgss_positive_test=patients.with_test_result_in_sgss(
        pathogen="SARS-CoV-2",
        test_result="positive",
        find_first_match_in_period=True,
        returning="date",
        date_format="YYYY-MM-DD",
        return_expectations={"date": {"earliest": "2020-03-01"}},
    ),


    # Outcomes
    died_ons_covid=patients.with_these_codes_on_death_certificate(
        codes_covid_death,
        returning="binary_flag",
        on_or_after=from_date,
        match_only_underlying_cause=False,
        return_expectations={"date": {"earliest": "2020-03-01"}},
    ),
    died_ons_covid_underlying=patients.with_these_codes_on_death_certificate(
        codes_covid_death,
        returning="binary_flag",
        on_or_after=from_date,
        match_only_underlying_cause=True,
        return_expectations={"date": {"earliest": "2020-03-01"}},
    ),
    died_ons=patients.died_from_any_cause(
        returning="binary_flag",
        on_or_after=from_date,
        return_expectations={"date": {"earliest": "2020-03-01"}},
    ),

    died_ons_noncovid = patients.satisfying(
        """(NOT died_ons_covid) AND died_ons""",
        return_expectations={"incidence": 0.15},
    ),

    death_category = patients.categorised_as(
        {
            "alive": "NOT died_ons",
            "covid-death": "died_ons_covid",
            "non-covid-death": "died_ons_noncovid",
            "unknown" : "DEFAULT"
        },
        return_expectations={"category": {"ratios": {"alive": 0.8, "covid-death": 0.1, "non-covid-death": 0.1}}},
    ),

    date_died_ons=patients.died_from_any_cause(
        returning="date_of_death",
        on_or_after=from_date,
        date_format="YYYY-MM-DD",
        return_expectations={"date": {"earliest": "2020-03-01"}},
    ),

)