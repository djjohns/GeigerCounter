# GeigerCounter

Quick and dirty dashboard for the 
[GQ GMC-SE Geiger Counter](https://www.gqelectronicsllc.com/comersus/store/comersus_viewItem.asp?idProduct=5845) using [Streamlit](https://docs.streamlit.io/), [pandas](https://pandas.pydata.org/docs/), [plotly](https://plotly.com/python/), [pygmc](https://github.com/Wikilicious/pygmc), [schedule](https://pypi.org/project/schedule/), [Postgres](https://pypi.org/project/psycopg2-binary/), and [docker](https://www.docker.com/). 

![Screenshot of GQ GMC-SE Dashboard](./img/Screenshot1.png)
![Screenshot of GQ GMC-SE Dashboard](./img/Screenshot2.png)

## Dockerized

This app has now been dockerized.

You will need to create two env files.

**NOTE:** Make sure you change the change the user name and password in the env 
files!

Create your .env file in the root directory of the project.
```
# .env

 # --- App DB connection (gmc-dashboard) ---
PGHOST=db            # service name in compose network
PGPORT=5432
PGDATABASE=gmc
PGUSER=gmc
PGPASSWORD=CHANGE_ME
DATABASE_URL=postgresql+psycopg2://gmc:CHANGE_ME@db:5432/gmc

# App settings
GMC_TABLE=public.gmc_readings
TZ=America/Chicago
```
Create your db.env file in the root directory of the project.
```
# db.env

# --- Postgres container (db) ---
POSTGRES_DB=gmc
POSTGRES_USER=gmc
POSTGRES_PASSWORD=CHANGE_ME
CSV_DIR=/docker-entrypoint-initdb.d/seed
GMC_TABLE=public.gmc_readings
```

Now that the env files have been created you can run the command:
```bash
docker-compose up --build
```

This will build and run the containers required for this app.

**Note:** If you have some csv files to preload the database you can drop them in the ``/data/`` directory and they will be picked up and loaded to the Postgres db after the ``init.sql`` script runs when the Postgres container and volume are built in the docker compose process.

## To use this dashboard locally

Clone the repo:
```bash
git clone https://github.com/djjohns/GeigerCounter.git
```

Install the dependencies:
```bash
pip install -r requirements.txt
```

Run the get_device_log.py script:
```bash
python get_device_log.py
```

This will write a csv file to the data directory in the repo called 
``GMC-SE_YYYYMMDD.csv``

Run the Streamlit app:
```bash
streamlilt run app.py
```

This should automatically open up the dashboard in your default browser. If not
the dashboard can be found at:
http://localhost:8501/

Once the dashboard is up and running you can upload the csv file that was 
created earlier or point the dashboard to the filepath to where the file is 
located.

This is by no means a production ready app and should be treated as such. Once 
again this is just something quick and dirty to replace the 90's era interface 
that the is provided from the device's manufacture.


# Added scheduled scripts for QOL

[daily_reset_device_log.py](./scripts/daily_reset_device_log.py): Resets the device's internal log daily at 23:59. This reset is a bit clunky as you have to use the pygmc's ``send_key`` method in [erase_history.py](./scripts/utilities/erase_history.py) to cycle through the device menu to erase the saved history on the device. The easiest thing I could think of is to cycle through the simulated key strokes, then get the devices history to check the row count and if the row count was greater than 1 to call the [erase_history](./scripts/utilities/erase_history.py) function again. This would be better if I could get the boolean value displayed on the menu when erasing the history.

[daily_live_file.py](./scripts/daily_live_file.py): Calls the [get_device_log.py](./scripts/utilities/get_device_log.py) every minute. This is handy for the live feed for the dashboard. Just point to the daily_filepath and the dashboard updates every 10 seconds. The script is scheduled to run every minute, as that is what I have my GMC-SE set to log anyhow.