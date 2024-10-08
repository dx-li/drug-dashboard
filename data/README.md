# Michigan Drug Database

## Overview
This database is contains data on controlled prescription drugs from the state of Michigan, with a focus on prescription data across different regions, patient demographics, and prescription characteristics. It is sourced from [https://www.michigan.gov/lara/bureau-list/bpl/health/maps/reports](https://www.michigan.gov/lara/bureau-list/bpl/health/maps/reports). It consists of two primary tables: `patient` and `patient_with_age`. Each captures key information about medication prescriptions in hospitals, including drug schedules, patient location, and prescription details.

## Schema

### 1. `patient`
This table contains prescription data aggregated at the level of patient location (county and state) for the years **2013-2022**.

| Column Name            | Description                                                                 |
|------------------------|-----------------------------------------------------------------------------|
| `PATIENT_COUNTY`        | The county where the patient resides                                         |
| `PATIENT_STATE`         | The state where the patient resides                                          |
| `DRUG_NAME_STRENGTH`    | The name of the prescribed drug, including its strength                     |
| `DEA_DRUG_SCHEDULE`     | The drug’s classification under the DEA’s controlled substance schedule      |
| `AHFS_DESCRIPTION`      | The description of the drug based on AHFS (American Hospital Formulary Service) classification |
| `PRESCRIPTION_COUNT`    | The number of prescriptions written for the drug                            |
| `PRESCRIPTION_QUANTITY` | The total quantity of the drug prescribed, measured in **dosage units**      |
| `Year`                  | The year the data corresponds to                                             |

### 2. `patient_with_age`
This table contains the same information as the `patient` table but with additional details such as age ranges and ZIP codes. Data for this table spans **2018-2022**.

| Column Name                                                | Description                                                                                               |
|------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------|
| `PATIENT_COUNTY`                                            | The county where the patient resides                                                                       |
| `PATIENT_STATE`                                             | The state where the patient resides                                                                        |
| `AGE_RANGE`                                                 | The age group of the patient ('Ages 4 and younger', 'Ages 5 To 17', 'Ages 18 To 24', 'Ages 25 To 34', 'Ages 35 To 44', 'Ages 45 To 54', 'Ages 55 To 64', 'Ages 65 and older')                                                    |
| `DRUG_NAME_STRENGTH`                                        | The name of the prescribed drug, including its strength                                                    |
| `DEA_DRUG_SCHEDULE`                                         | The drug’s classification under the DEA’s controlled substance schedule                                    |
| `AHFS_DESCRIPTION`                                          | The description of the drug based on AHFS classification                                                   |
| `PRESCRIPTION_COUNT`                                        | The number of prescriptions written for the drug                                                           |
| `PRESCRIPTION_QUANTITY`                                     | The total quantity of the drug prescribed, measured in **dosage units**                                    |
| `PATIENT_COUNT`                                             | The number of unique patients receiving the drug                                                           |
| `AVERAGE_DAYS_SUPPLY`                                       | The average number of days supply for prescriptions issued                                                 |
| `DAYS_SUPPLY`                                               | The total days of drug supply provided                                                                     |
| `AVERAGE_DAILY_MMEs`                                        | The average daily dose of the drug in morphine milligram equivalents (MMEs). **Only calculated for opiate agonists and partial agonists**. |
| `PRESCRIPTION_COUNT_GREATER_THAN_OR_EQUAL_TO_90_MMEs`       | The count of prescriptions where the daily dose is greater than or equal to 90 MMEs. **Only calculated for opiate agonists and partial agonists**. |
| `Year`                                                      | The year the data corresponds to                                                                           |
| `PATIENT_ZIP`                                               | The ZIP code of the patient. **This data is available from 2021 onwards**                                   |
