from cohortextractor import StudyDefinition, patients, Measure


## CODE LISTS
# All codelist are held within the codelist/ folder.
from codelists import *
from config import m, min_days, n

## STUDY POPULATION
# Defines both the study population and points to the important covariates

study = StudyDefinition(
    index_date="2020-03-01",
    default_expectations={
        "date": {"earliest": "1970-01-01", "latest": "today"},
        "rate": "uniform",
        "incidence": 0.2,
    },
    # This line defines the study population
    population=patients.registered_as_of("index_date"),

    sgss_positive=patients.with_test_result_in_sgss(
                pathogen="SARS-CoV-2",
                test_result="positive",
                restrict_to_earliest_specimen_date=False,
                returning="binary_flag",
                on_or_before="index_date",
                return_expectations={
                    "incidence": 0.75,
                },
            ),
    primary_care_positive=patients.with_these_clinical_events(
                codes_probable_covid_pos_test,
                returning="binary_flag",
                on_or_before="index_date",
                return_expectations={
                    "incidence": 0.75,
                },
            ),
    covid_admission=patients.admitted_to_hospital( 
        with_these_diagnoses=covid_icd10, 
        returning="binary_flag",
        on_or_before="index_date",
        return_expectations={
            "incidence": 0.75,
        },   ),

    positive_any=patients.satisfying(
        """
        covid_admission OR
        primary_care_positive OR
        sgss_positive 
        """ 
    ),

)

measures = [
    Measure(
        id="sgss_positive_rate",
        numerator="sgss_positive",
        denominator="population",
        group_by=["population"],
    ),

    Measure(
        id="primary_care_positive_rate",
        numerator="primary_care_positive",
        denominator="population",
        group_by=["population"],
    ),

    Measure(
        id="covid_admission_positive_rate",
        numerator="covid_admission",
        denominator="population",
        group_by=["population"],
    ),

    Measure(
        id="any_positive_rate",
        numerator="positive_any",
        denominator="population",
        group_by=["population"],
    ),
]