from cohortextractor import (
    StudyDefinition,
    codelist,
    codelist_from_csv,
    filter_codes_by_category,
    patients,
)

## CODE LISTS
# All codelist are held within the codelist/ folder.
from codelists import *
from config import m, min_days, n


# gp_consultation_date_X: Creates n columns for each consecutive GP consulation date
def date_X(codes, n):
    def var_signature(name, on_or_after):
        return {
            name: patients.with_these_clinical_events(
                globals()[codes],
                returning="date",
                on_or_after=on_or_after,
                date_format="YYYY-MM-DD",
                find_first_match_in_period=True,
                return_expectations={
                    "date": {"earliest": from_date, "latest": to_date},
                    "incidence": 1 / i,  # to help check events_pp in counts.py works
                },
            ),
        }

    for i in range(1, n + 1):
        if i == 1:
            variables = var_signature(f"{codes[6:]}_X1_date", "index_date")
        else:
            variables.update(
                var_signature(
                    f"{codes[6:]}_X{i}_date",
                    f"{codes[6:]}_X{i-1}_date + {min_days} days",
                )
            )
    return variables


def sgss_X(n):
    def var_signature(name, on_or_after):
        return {
            name: patients.with_test_result_in_sgss(
                pathogen="SARS-CoV-2",
                test_result="positive",
                restrict_to_earliest_specimen_date=False,
                returning="date",
                on_or_after=on_or_after,
                date_format="YYYY-MM-DD",
                find_first_match_in_period=True,
                return_expectations={
                    "date": {"earliest": from_date, "latest": to_date},
                    "incidence": 1 / i,
                },
            ),
        }

    for i in range(1, n + 1):
        if i == 1:
            variables = var_signature(f"sgss_positive_test_X1_date", "index_date")
        else:
            variables.update(
                var_signature(
                    f"sgss_positive_test_X{i}_date",
                    f"sgss_positive_test_X{i-1}_date + {min_days} days",
                )
            )
    return variables


## STUDY POPULATION
# Defines both the study population and points to the important covariates


from_date = "2020-02-01"
to_date = "2021-11-28"

study = StudyDefinition(
    index_date=from_date,
    default_expectations={
        "date": {"earliest": "1970-01-01", "latest": "today"},
        "rate": "uniform",
        "incidence": 0.2,
    },
    # This line defines the study population
    population=patients.registered_with_one_practice_between(from_date, to_date),
    # demographic info
    # https://github.com/ebmdatalab/tpp-sql-notebook/issues/33
    age=patients.age_as_of(
        from_date,
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
        from_date,
        returning="index_of_multiple_deprivation",
        round_to_nearest=100,
        return_expectations={
            "rate": "universal",
            "category": {"ratios": {"100": 0.1, "200": 0.2, "300": 0.7}},
        },
    ),
    # https://github.com/ebmdatalab/tpp-sql-notebook/issues/54
    stp=patients.registered_practice_as_of(
        from_date,
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
        from_date,
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
    # covid-related code dates
    **date_X("codes_antigen_negative", n=m),
    **date_X("codes_exposure_to_disease", n=n),
    **date_X("codes_historic_covid", n=n),
    **date_X("codes_potential_historic_covid", n=m),
    **date_X("codes_probable_covid", n=m),
    **date_X("codes_probable_covid_pos_test", n=n),
    **date_X("codes_probable_covid_sequelae", n=n),
    **date_X("codes_suspected_covid_advice", n=m),
    **date_X("codes_suspected_covid_had_test", n=m),
    **date_X("codes_suspected_covid_isolation", n=n),
    **date_X("codes_suspected_covid_nonspecific", n=n),
    **date_X("codes_suspected_covid", n=m),
    **date_X("codes_covid_unrelated_to_case_status", n=m),
    **date_X("codes_suspected_covid_had_antigen_test", n=n),
    **sgss_X(n=n),
    # Outcomes
    died_ons_covid=patients.with_these_codes_on_death_certificate(
        codes_covid_death,
        returning="binary_flag",
        on_or_after=from_date,
        match_only_underlying_cause=False,
        return_expectations={"date": {"earliest": from_date}},
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
        return_expectations={"date": {"earliest": from_date}},
    ),
    died_ons_noncovid=patients.satisfying(
        """(NOT died_ons_covid) AND died_ons""",
        return_expectations={"incidence": 0.15},
    ),
    death_category=patients.categorised_as(
        {
            "alive": "NOT died_ons",
            "covid-death": "died_ons_covid",
            "non-covid-death": "died_ons_noncovid",
            "unknown": "DEFAULT",
        },
        return_expectations={
            "category": {
                "ratios": {"alive": 0.8, "covid-death": 0.1, "non-covid-death": 0.1}
            }
        },
    ),
    date_died_ons=patients.died_from_any_cause(
        returning="date_of_death",
        on_or_after=from_date,
        date_format="YYYY-MM-DD",
        return_expectations={"date": {"earliest": from_date}},
    ),
)
