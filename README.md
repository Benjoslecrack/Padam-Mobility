# PADAM Data Engineering Test

## Table of content

- [PADAM Data Engineering Test](#padam-data-engineering-test)
  - [Table of content](#table-of-content)
  - [About](#about)
    - [Context](#context)
    - [Repo architecture](#repo-architecture)
    - [Set up](#set-up)
  - [What you are asked for](#what-you-are-asked-for)
    - [What will be evaluated](#what-will-be-evaluated)
    - [Some general guidelines](#some-general-guidelines)
  - [Some utilities](#some-utilities)

## About

### Context

The trainee has left without finishing his project. In 6 months, he implemented
the tools to simulate data created in our production database.

So you take over. Unfortunately, it has to work tonight! Sorry for the short
notice.

The `production_data` postgres database contains a table `entity` with a `created_at`
(timestamp) and a `value` (int).

We want to fetch data on a monthly basis, ingest them into a `warehouse` postgres
database, transform it, and build exports in csv format to gather aggregates on
different time scale (daily, montly, yearly) for the business team.

### Repo architecture

This repo contains a `docker-compose.yml` file which will spawn
the needed services:

* `production_data` where the entity table will be created
* `warehouse_data` where you will ingest the data
* `pg_admin` to check the schemas and content of the dbs (for test / debug if you need)
* `data_tools` which will handle computations
    - Its build context is '.', using `./Dockerfile`

The `insert_all_data.sh` is the "main" script which does the following:

```sh
set -ex
for MONTH in 1 2 3 4 5 6 7 8 9 10 11 12
do
    # insert data for the specific month
    python scripts/insert_monthly_data.py $YEAR $MONTH
    # prepare all inserted data
    python scripts/data_preparation.py
    # export the data for the specific month
    python scripts/data_export.py $YEAR $MONTH
done
```

The `data_preparation.py` script doesn't take a `$MONTH` argument as it is supposed to
be idempotent. It could be run on a daily basis, if needed.

The exercice is about filling the `data_preparation.py` script and the `data_export.py`
script.

### Set up

You should have docker and docker-compose installed.

To start all containers:

    docker-compose up -d

The pg_admin should be accessible on http://0.0.0.0:4300, and the connections to the
databases are already set.

Refer to the `docker-compose.yml` file for the different passwords.

## What you are asked for

This test will be evaluated by running the `insert_all_data.sh` script, with the
`RANDOM_MAIN_CONTROLLER` from `scripts/insert_monthly_data.py` set to 100, and we will
evaluate the output in the folder `exports` :

    docker-compose run --rm data_tools sh insert_all_data.sh

If you want to control the quantity of data inserted from the command line:

    docker-compose run -e RANDOM_MAIN_CONTROLLER=1 --rm data_tools sh insert_all_data.sh

The `exports` folder should have a partitioned structure, with aggregated `csv` files:

```
- exports/
  - year={year}/
    - entity_stats_yearly_{year}.csv
    - month={month}/
        - entity_stats_monthly_{year}_{month}.csv
        - day={day}/
            - entity_stats_daily_{year}_{month}_{day}.csv
```

In each file, we have the `sum` , `min` , `max` , `mean` of the `entity.value`

over the specified time period. Here is the expected file columns:

```
entity_stats_yearly_{year}.csv -> 1 row

| year | sum_values | min_values | max_values | mean_values |

entity_stats_monthly_{year}_{month}.csv -> 1 row

| year | month | sum_values | min_values | max_values | mean_values |

entity_stats_daily_{year}_{month}_{day}.csv -> 1 row

| year | month | day | sum_values | min_values | max_values | mean_values |
```

In the `data_preparation.py` script:

    - Implement an incremental load into the `warehouse_data` postgres database
    - Implement as many transformations as possible in this data warehouse
        (views, tables...)

In the `data_exports.py` script:

    - Implement the exports for the specified month
    - Update the yearly stat export
    - optional: Update the `by_month` and `by_day` files

### What will be evaluated

We want to validate that you are familiar with some tools we are using on a daily basis
(docker, docker-compose, python).

And that you are able to write python code in the context of data manipulation.

We would like to see clean code, with clear logic.

The test should be replicable on our side (dependencies, tooling...).

The postgres named `warehouse` simulate a distant warehouse with a powerful and scalable
query engine, so we would prefer a ELT approach (tables, views, materialization...) over
a ETL one (computation in python / pandas).

### Some general guidelines

You shouldn't spend more than 2h on this test.

You should kind of "rush" to a working solution here.

Don't hésitate to share your `.git` folder.

If you feel your code is horrible or has strong limits, don't hesitate
to add `#TODO` comments to show us what code you would have written
if you had the time.
 
We will discuss this test with you during the following interview, but don't hesitate
to write a `COMMENTS.md` file where you explain what you did, the limits of your
implementation or whatever you want to share with us.

Feel free to modify any files from the test, add tooling (cli, makefile,
dependencies...).
The only thing that should stay as it is is the name of the `insert_all_data.sh` script
(the inside can change if you want).

## Some utilities

If you want to clean up all data, and start from scratch, 
don't forget the docker volumes:

    docker-compose down --volumes --remove-orphans

You can run as many time as you want `insert_monthly_data.py`

because the data is first deleted, and generated with fixed
seeds to get replication.
