
# PURPOSE: This script is used to update all existing records in the rmi_pbi_activity.activity_log 
#          table with the latest cost center information from the rmi_skills.worker_details table

import pandas as pd
from pathlib import Path
import sqlalchemy
from dotenv import load_dotenv
import os
from datetime import date, timezone, datetime
from sqlalchemy import text   # May need this if using newer version of sqlalchemy


load_dotenv('cred.env') # Location of environments file
rmi_db = os.getenv('DBASE_PWD') # Password for RMI Azure for MySQL environment
rmi_db_ip = os.getenv('DBASE_IP') # Server IP for RMI Azure for MySQL environment
ssl_file = 'C:/Users/ghoffman/OneDrive - RMI/01. Projects/DigiCertGlobalRootCA.crt.pem' # Location of digital SSL cert file

mydir = Path('M365_activity/pbi_activity_data/') # Folder where Powershell script outputs JSON files
destinationpath = 'M365_activity/pbi_activity_data/archive/' # Archive folder for JSONs after importing and appending
file_raw_backup = 'M365_activity/pbi_activity_data/imports/raw_'+ str(date.today()) + '.xlsx' # Raw backup file path
file_import = 'M365_activity/pbi_activity_data/imports/import_'+ str(date.today()) + '.xlsx' # Import-formatted backup file path

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

df_staff['email'] = df_staff['email'].str.lower()


# Extract existing records from activity_log table
database_username = 'rmiadmin'
database_password = rmi_db
database_ip       = rmi_db_ip
database_name     = 'rmi_pbi_activity'
connect_args={'ssl_ca':ssl_file}
connect_string = 'mysql+mysqlconnector://{0}:{1}@{2}/{3}'.format(database_username, database_password, 
                                                      database_ip, database_name)
database_connection = sqlalchemy.create_engine(connect_string,connect_args=connect_args) 

with database_connection.connect() as conn:
    result = conn.execute(text("select * from activity_log"))
    df1 = pd.DataFrame(result.fetchall())
    df1.columns = result.keys()

# create backup of raw data
df1.to_excel(file_raw_backup)

df_import = df1.copy()

df_import['UserId'] = df_import['UserId'].str.lower()
df_import.drop(columns=['UserProgram'], inplace=True)

# add cost center to df_import
df_import = df_import.merge(df_staff, how='left', left_on='UserId', right_on='email')

# Drop email column
df_import.drop(columns=['email'], inplace=True)
#df_import.rename(columns={'UserProgram_y':'UserProgram'}, inplace=True)

# Save local copy of import-formatted data
df_import.to_excel(file_import)

# delete all records from activity_log
with database_connection.connect() as conn:
    result = conn.execute(text("delete from activity_log"))
    database_connection.dispose()

# Import new records
df_import.to_sql(con=database_connection, name='activity_log', if_exists='append', index=False)

# Close connections
database_connection.dispose()

