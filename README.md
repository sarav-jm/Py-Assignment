- [How to run the applications](#how-to-run-the-applications)
  - [Task 1 - ETL of semi-structured data](#task-1---etl-of-semi-structured-data)
    - [In widows OS](#in-widows-os)
    - [In  Linux OS](#in--linux-os)
  - [Task 2 - Beta Calculation](#task-2---beta-calculation)
    - [In widows OS](#in-widows-os-1)
    - [In  Linux OS](#in--linux-os-1)
- [Orders API](#orders-api)
- [Build and run docker](#build-and-run-docker)
- [Run Flask Server](#run-flask-server)
- [Examples](#examples)
    - [To Fetch order by given order number](#to-fetch-order-by-given-order-number)
    - [To List all orders by date range and ticker](#to-list-all-orders-by-date-range-and-ticker)
    - [To summarize order by order_id, ticker and date range (without fill_duration)](#to-summarize-order-by-order_id-ticker-and-date-range-without-fill_duration)
    - [To summarize order by order_id, ticker and date range (with fill_duration)](#to-summarize-order-by-order_id-ticker-and-date-range-with-fill_duration)

# How to run the applications

## Task 1 - ETL of semi-structured data
ETL the csv file to database, run the server & start serving the API

### In widows OS

1. Download and extract the file
2. Go to the folder path
```
    cd dist-package\windows
```
3. Run the following command to execute the Task1
```
    .\start_server_winx64.exe --csv-file C:\path\to\csv-file --db-file C:\path\to\db-file
```

Example:
```
    .\start_server_winx64.exe --csv-file C:\Users\Administrator\workspace\etl-and-beta-calc\app\data\firm_trades.csv --db-file C:\Users\Administrator\workspace\etl-and-beta-calc\app\my_lite_store1.db
```

### In  Linux OS
1. Download and extract the file
2. Go to the directory path
```
    cd dist-package/linux
```

3. Run the following command to execute the Task1
```
    ./start_server_linux --csv-file /absolute-path/to/csv-file --db-file C:\path\to\db-file
```

Example:
```
    ./start_server_linux --csv-file /home/username/project/app/data/firm_trades.csv --db-file /home/username/project/my_lite_store.db
```

## Task 2 - Beta Calculation
Read the Excel file and deliver the beta calculation as requested

### In widows OS
1. Download and extract the file
2. Go to the folder path
```
    cd dist-package\windows
```
3. Run the following command to execute the Task1
```
    .\beta_calc_win-x64.exe --excel-file C:\absolute-path\to\xlsx-file --as-of-date AS_OF_DATE [--window WINDOW] --frequency {daily,weekly,monthly,quarterly,bi-weekly}
```

Example:
```
    .\beta_calc_win-x64.exe --excel-file C:\Users\Administrator\data\task2_stock_data.xlsx --as-of-date 2021-10-31 --window 1y --frequency daily
```

### In  Linux OS
1. Download and extract the file
2. Go to the directory path
```
    cd dist-package/linux
```
3. Run the following command to execute the Task1
```
    ./beta_calc_linux --excel-file /absolute-path/to/xlsx-file --as-of-date AS_OF_DATE [--window WINDOW] --frequency {daily,weekly,monthly,quarterly,bi-weekly}
```

Example:
```
    ./beta_calc_linux --excel-file /home/username/project/app/data/task2_stock_data.xlsx --as-of-date 2021-10-31 --window 1y --frequency daily
```

# Orders API

## Orders operations <!-- omit in toc -->

### Fetch order by given order number <!-- omit in toc -->

    GET ​/orders​/get​/{id}

**Parameters**

|Name |Type   |Description         |
|-----|-------|--------------------|
|`id`*|integer|The order identifier| <!-- omit in toc -->

---
### List all orders by date range and ticker <!-- omit in toc -->

    GET ​/orders​/search

**Query Parameters**

|Name        |Type         |Description     |
|------------|-------------|----------------|
|`date_from`*|string($date)|(eg: 2020-12-01)| <!-- omit in toc -->
|`date_to`*  |string($date)|(eg: 2020-12-31)| <!-- omit in toc -->
|`ticker`*   |string       |(eg: OBJY)      | <!-- omit in toc -->

---

### Shows a summary of all orders by date_from and date_to range with order_id and ticker values <!-- omit in toc -->

    GET ​/orders​/summary

**Query Parameters**

|Name        |Type         |Description     |
|------------|-------------|----------------|
|`order_id`* |integer      |(eg: 3520557)   |
|`ticker`*   |string       |(eg: OBJY)      |
|`date_from`*|string($date)|(eg: 2020-12-01)|
|`date_to`*  |string($date)|(eg: 2020-12-31)|


#### *parameters are mandatory. All response content-type is `application/json` only <!-- omit in toc -->

# Build and run docker

#### follow `bin/docs.sh` to build and run docker <!-- omit in toc -->

# Run Flask Server
#### after docker build and ran get bash into docker by `./bin/docker_bash.sh` then <!-- omit in toc -->
    python app/run.py
#### it runs the flask server in default port 4444 <!-- omit in toc -->


# Examples

#### Open terminal and run these following commands <!-- omit in toc -->

### To Fetch order by given order number
    curl -X GET -H "Content-Type: application/json" "http://localhost:4444/orders/get/3520680"

### To List all orders by date range and ticker
    curl -X GET -H "Content-Type: application/json" "http://localhost:4444/orders/search?date_from=2022-06-01&date_to=2022-06-30&ticker=FNOE"

### To summarize order by order_id, ticker and date range (without fill_duration)
    curl -X GET -H "Content-Type: application/json" "http://localhost:4444/orders/summary?date_from=2022-06-01&date_to=2022-06-30&ticker=OBJY&order_id=3520557"

### To summarize order by order_id, ticker and date range (with fill_duration)
    curl -X GET -H "Content-Type: application/json" "http://localhost:4444/orders/summary?date_from=2022-06-01&date_to=2022-06-30&order_id=3520680&ticker=FNOE"

