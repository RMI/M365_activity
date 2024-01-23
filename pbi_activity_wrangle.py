## FORMAT POWER BI ACTIVITY LOG DATA
## Purpose: This py script reformats JSON files extracted via PowerShell for RMI Power BI utilization, then imports the data to the rmi_pbi_activity MySQL schema
## Dependencies: 
##      - Must have Power BI Admin user role assigned in MS365
##      - Must have access to KM Azure for MySQL environment
##      - Must be present during file execution to confirm admin credential utilization
##      - Must have KM Azure server IP added to local host file (Requires admin credentials)
##      - Must have SSL CA.crt.pem file

import pandas as pd
from pathlib import Path
import sqlalchemy
from dotenv import load_dotenv
import os
import mysql.connector
from datetime import date, timezone, datetime
import shutil
import subprocess
import sys
from sqlalchemy import text   # May need this if using newer version of sqlalchemy


# Execute Powershell script to extract Power BI info from MS Graph. Requires Power BI admin account. User will be prompted to sign-in
p = subprocess.Popen('powershell.exe -ExecutionPolicy RemoteSigned -file "M365_activity\\ps_pbi_activity_get.ps1"', stdout=sys.stdout)

load_dotenv('cred.env') # Location of environments file
rmi_db = os.getenv('DBASE_PWD') # Password for RMI Azure for MySQL environment
rmi_db_ip = os.getenv('DBASE_IP') # Server IP for RMI Azure for MySQL environment
ssl_file = 'C:/Users/ghoffman/OneDrive - RMI/01. Projects/DigiCertGlobalRootCA.crt.pem' # Location of digital SSL cert file

mydir = Path('M365_activity/pbi_activity_data/') # Folder where Powershell script outputs JSON files
#sourcepath='M365_activity/pbi_activity_data/' 
destinationpath = 'M365_activity/pbi_activity_data/archive/' # Archive folder for JSONs after importing and appending
file_raw_backup = 'M365_activity/pbi_activity_data/imports/raw_'+ str(date.today()) + '.xlsx' # Raw backup file path
file_import = 'M365_activity/pbi_activity_data/imports/import_'+ str(date.today()) + '.xlsx' # Import-formatted backup file path

###################################################################
######### BELOW THIS LINE DOES NOT REQUIRE MODIFICATION ###########
###################################################################

# Get list of current RMI staff emails and cost centers

database_username = 'rmiadmin'
database_password = rmi_db
database_ip       = rmi_db_ip
database_name     = 'rmi_skills'
database_connection = sqlalchemy.create_engine('mysql+mysqlconnector://{0}:{1}@{2}/{3}'.
                                               format(database_username, database_password, 
                                                      database_ip, database_name))



query_string = "select email, cost_center from worker_details"

with database_connection.connect() as conn:
    result = conn.execute(text(query_string))
    df_staff = pd.DataFrame(result.fetchall())
    df_staff.columns = result.keys()
    database_connection.dispose()

df_staff.rename(columns={'cost_center':'UserProgram'}, inplace=True)


# Create blank dfs list and df_base for appending data from JSONs
dfs = []

df_base = pd.DataFrame(columns= ['Id', 'CreationTime', 'Operation', 'UserType', 'UserId','Activity', 'ItemName', 'WorkSpaceName', 'DatasetName',
                 'ReportName', 'CapacityName', 'ObjectId','ArtifactName','DistributionMethod', 'ConsumptionMethod', 'ArtifactKind',
                   'DashboardName', 'SharingAction','SharingScope' ])

# Loop through data folder, appending any JSON files to df
for file in mydir.glob('*.json'):
    data = pd.read_json(file, encoding='utf-16')
    dfs.append(data)

df = pd.concat(dfs, ignore_index=True)

df = pd.DataFrame(df)

df1 = pd.concat([df_base, df], ignore_index=True)

# Move new JSONs to archive
sourcefiles = os.listdir(mydir)
for file in sourcefiles:
    if file.endswith('.json'):
        shutil.move(os.path.join(mydir,file), os.path.join(destinationpath,file))

# Export Excel backup
df1.to_excel(file_raw_backup)

# Format data for database import
df_import = df1[['Id', 'CreationTime', 'Operation', 'UserType', 'UserId','Activity', 'ItemName', 'WorkSpaceName', 'DatasetName',
                 'ReportName', 'CapacityName', 'ObjectId','ArtifactName','DistributionMethod', 'ConsumptionMethod', 'ArtifactKind',
                   'DashboardName', 'SharingAction','SharingScope' ]]

df_import = df_import[df_import['Id'].notnull()]
df_import['CreationTime'] = pd.to_datetime(df_import['CreationTime'], format="%Y-%m-%dT%H:%M:%SZ")
df_import.drop_duplicates(subset='Id', inplace=True)

# Extract existing record IDs and compare, removing duplicates
database_username = 'rmiadmin'
database_password = rmi_db
database_ip       = rmi_db_ip
database_name     = 'rmi_pbi_activity'
connect_args={'ssl_ca':ssl_file}
connect_string = 'mysql+mysqlconnector://{0}:{1}@{2}/{3}'.format(database_username, database_password, 
                                                      database_ip, database_name)
database_connection = sqlalchemy.create_engine(connect_string,connect_args=connect_args) 

with database_connection.connect() as conn:
    result = conn.execute(text("select Id from activity_log")) #May need this if using a more recent version of sqlalchemy
   # result = conn.execute("select Id from activity_log")
    df1 = pd.DataFrame(result.fetchall())
    df1.columns = result.keys()

df_import.set_index('Id')
df_import = df_import.drop(df_import[df_import.Id.isin(df1['Id'])].index.tolist())
df_import.reset_index(inplace=True)
df_import = df_import.drop("index", axis= 1)

df_import['CreationTime'] = df_import['CreationTime'].dt.tz_localize(None)

# add cost center to df_import
df_import = df_import.merge(df_staff, how='left', left_on='UserId', right_on='email')

# Drop email column
df_import.drop(columns=['email'], inplace=True)

# Save local copy of import-formatted data
df_import.to_excel(file_import)
# Import new records
df_import.to_sql(con=database_connection, name='activity_log', if_exists='append', index=False)

# Close connections
database_connection.dispose()