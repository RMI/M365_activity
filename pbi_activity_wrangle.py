## FORMAT POWER BI ACTIVITY LOG DATA
## Purpose: This py script reformats JSON files extracted via PowerShell for RMI Power BI utilization, then imports the data to the rmi_pbi_activity MySQL schema
## Dependencies: Must execute powershell.txt in PowerShell to generate JSON files

import pandas as pd
from pathlib import Path
import sqlalchemy
from dotenv import load_dotenv
import os
import mysql.connector
from datetime import date, timezone, datetime
import shutil

load_dotenv('cred.env')
rmi_db = os.getenv('DBASE_PWD')
rmi_db_ip = os.getenv('DBASE_IP')

mydir = Path("pbi_activity_data/")
dfs = []

df_base = pd.DataFrame(columns= ['Id', 'CreationTime', 'Operation', 'UserType', 'UserId','Activity', 'ItemName', 'WorkSpaceName', 'DatasetName',
                 'ReportName', 'CapacityName', 'ObjectId','ArtifactName','DistributionMethod', 'ConsumptionMethod', 'ArtifactKind',
                   'DashboardName', 'SharingAction','SharingScope' ])

# Loop through data folder, appending any JSON files to df
for file in mydir.glob('*.json'):
    data = pd.read_json(file,  encoding='utf-16')
    dfs.append(data)

df = pd.concat(dfs, ignore_index=True)

df = pd.DataFrame(df)

df1 = pd.concat([df_base, df], ignore_index=True)

# Move new JSONs to archive
sourcepath='pbi_activity_data/'
sourcefiles = os.listdir(sourcepath)
destinationpath = 'pbi_activity_data/archive/'
for file in sourcefiles:
    if file.endswith('.json'):
        shutil.move(os.path.join(sourcepath,file), os.path.join(destinationpath,file))

# Export Excel backup
name = 'pbi_activity_data/imports/raw_'+ str(date.today()) + '.xlsx'
df1.to_excel(name)

# Format data for database import
df_import = df1[['Id', 'CreationTime', 'Operation', 'UserType', 'UserId','Activity', 'ItemName', 'WorkSpaceName', 'DatasetName',
                 'ReportName', 'CapacityName', 'ObjectId','ArtifactName','DistributionMethod', 'ConsumptionMethod', 'ArtifactKind',
                   'DashboardName', 'SharingAction','SharingScope' ]]

df_import = df_import[df_import['Id'].notnull()]
df_import['CreationTime'] = pd.to_datetime(df_import['CreationTime'], format="%Y-%m-%d %H:%M:%S")
df_import.drop_duplicates(subset='Id', inplace=True)

# Extract existing record IDs and compare, removing duplicates
database_username = 'rmiadmin'
database_password = rmi_db
database_ip       = rmi_db_ip
database_name     = 'rmi_pbi_activity'
database_connection = sqlalchemy.create_engine('mysql+mysqlconnector://{0}:{1}@{2}/{3}'.
                                               format(database_username, database_password, 
                                                      database_ip, database_name))

with database_connection.connect() as conn:
    result = conn.execute("select Id from activity_log")
    df1 = pd.DataFrame(result.fetchall())
    df1.columns = result.keys()

df_import.set_index('Id')
df_import = df_import.drop(df_import[df_import.Id.isin(df1['Id'])].index.tolist())
df_import.reset_index(inplace=True)
df_import = df_import.drop("index", axis= 1)

name = 'pbi_activity_data/imports/import_'+ str(date.today()) + '.xlsx'
df_import['CreationTime'] = df_import['CreationTime'].dt.tz_localize(None)

df_import.to_excel(name)
# Import new records
df_import.to_sql(con=database_connection, name='activity_log', if_exists='append', index=False)

# Close connections
database_connection.dispose()