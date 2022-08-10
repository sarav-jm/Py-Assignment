#!/usr/bin/env python
# coding: utf-8

# ### ETL initialization with pandas and numpy
import pandas as pd


def extract_load_transform(csv_file_path, disk_engine, is_db_found=False):
    # ### pandas read CSV file: `firm_trades.csv`
    # ##### first 3 rows are header values (ORDER, ROUTE, FILL) with respective column names
    print('Extracting CSV file from location[`%s`]...' % csv_file_path)
    df = pd.read_csv(csv_file_path)
    df.head()

    # ### Column names changes for Sqlite column stanard
    cols_df = df[:2].T.reset_index()
    cols_df.columns = cols_df[:1].values.tolist()[0]
    cols_df = cols_df[1:]
    cols_df = cols_df.applymap(lambda _c: str(_c).lower().replace(' ', '_'))

    # ### Separating data based on the row types ('ORDER', 'FILL', 'ROUTE')
    # ##### also applying Datatypes for each columns
    print('Transforming and applying datatypes...')
    extracted_df = {}
    df_dtypes = {
        'ROUTE': {'order_id': int, 'route_number': int, 'routed_amount': int, 'route_filled_amount': int, 'route_avg_price': float, 'route_comm_amount': int, 'route_comm_rate': int},
        'FILL': {'order_id': int, 'route_number': int, 'fill_amount': int, 'fill_price': float, 'exec_seq_num': int, 'prev_exec_seq_num': int, 'trader_uuid': int},
        'ORDER': {'order_id': int, 'amount': float, 'working_amount': int, 'filled_amount': int, 'average_price': float, 'trader_uuid': int, 'limit_price': float}
    }

    for c in ['ORDER', 'FILL', 'ROUTE']:
        r_df = df[2:]
        r_df.set_index(r_df.columns[0], inplace=True)
        r_df.columns = cols_df[c].values.tolist()
        r_df.rename(columns={'order_number': 'order_id'}, inplace=True)
        r_df = r_df[r_df.index == c]
        r_df.reset_index(inplace=True)
        del r_df["ORDER"]
        r_df = r_df.astype(df_dtypes[c])
        extracted_df.setdefault(c, r_df)

    def filter_df(_df):
        return _df[filter(lambda _c: str(_c) != 'nan', _df.columns)]

    # ### Separated df are stored in different variables
    order_df = filter_df(extracted_df['ORDER'])
    route_df = filter_df(extracted_df['ROUTE'])
    fill_df = filter_df(extracted_df['FILL'])

    # ### Creating datetime columns from date, time columns with timezone `America/New_York`
    order_df['create_date_time'] = pd.to_datetime(
        order_df["create_date"] + ' ' + order_df["create_time"]).dt.tz_localize('America/New_York').apply(lambda d: d.isoformat())
    order_df.drop(["create_date", "create_time"], axis=1, inplace=True)

    fill_df['fill_as_of_date_time'] = pd.to_datetime(
        fill_df["fill_as_of_date"] + ' ' + fill_df["fill_as_of_time"]).dt.tz_localize('America/New_York').apply(lambda d: d.isoformat())
    fill_df.drop(["fill_as_of_date", "fill_as_of_time"], axis=1, inplace=True)

    route_df['route_as_of_date_time'] = pd.to_datetime(
        route_df["route_as_of_date"] + ' ' + route_df["route_as_of_time"]).dt.tz_localize('America/New_York').apply(lambda d: d.isoformat())
    route_df.drop(["route_as_of_date", "route_as_of_time"],
                  axis=1, inplace=True)

    # ### Creating and Inserting tables for each row types ('ORDER', 'FILL', 'ROUTE')

    print((is_db_found and "Inserting" or "Creating and Inserting") +
          ' `ORDER` type rows into `order_table`...')
    order_df.to_sql('order_table', disk_engine,
                    if_exists='append', index=False)

    print((is_db_found and "Inserting" or "Creating and Inserting") +
          ' `FILL` type rows into `fill_table`...')
    fill_df.to_sql('fill_table', disk_engine, if_exists='append', index=False)

    print((is_db_found and "Inserting" or "Creating and Inserting") +
          ' `ROUTE` type rows into `route_table`...')
    route_df.to_sql('route_table', disk_engine,
                    if_exists='append', index=False)
