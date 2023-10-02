set -ex
for YEAR in 2022 2023
do
    for MONTH in 1 2 3 4 5 6 7 8 9 10 11 12
    do
        # insert data for the specific month
        python scripts/insert_monthly_data.py $YEAR $MONTH
        # prepare all inserted data
        python scripts/data_preparation.py
        # export the data for the specific month
        python scripts/data_export.py $YEAR $MONTH
    done
done
