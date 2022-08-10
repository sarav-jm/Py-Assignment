ACTION_NAME=$1
CSV_FILE=$2
DB_FILE=my_lite_store.db
APP_PY_VENV=search-app-env

installAppRequirements(){
  echo "INSTALL"
  echo "python version"
  python3 --version
  pip3 install virtualenv
  python3 -m virtualenv search-app-env
  source $APP_PY_VENV/bin/activate
# .\$APP_PY_VENV\Scripts\activate
  pip3 install -r requirements.txt
}

loadData(){
  echo "LOADDATA"
  source $APP_PY_VENV/bin/activate
  echo "$CSV_FILE"
  echo "$DB_FILE"
  python3 etl-process.py --csv-file $CSV_FILE --db-file $DB_FILE
}

runServer(){
  source $APP_PY_VENV/bin/activate
  which python3
  python3 run.py --db-file $DB_FILE
}

if [ "${ACTION_NAME}"  == "install" ]; then
    installAppRequirements
fi

if [ "${ACTION_NAME}"  == "loaddata" ]; then
    loadData
fi

if [ "${ACTION_NAME}"  == "runserver" ]; then
    runServer
fi

