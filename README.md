# M365_activity

## Purpose: Extract Power BI Activity Log data weekly to construct a historical database

 
**Dependencies**

- Have Power BI Admin user role assigned in MS365
- Have access to KM Azure for MySQL environment
- Must be present during file execution to confirm admin credential utilization


**Process**

- Every Monday at 9:00 AM ET, execute pbi_activity_wrangle.py
    - You will be prompted to login with an MS365 account. Use your Power BI admin account
    - You must be connected to the RMI VPN before executing the script.
    - If you are unable to run the script on Monday, you can simply modify the date range at the top of ps_pbi_activity_get.ps1 to a different number of days (default is a 7 day look back)
- Confirm data update in MySQL
- Confirm data update in Power BI Usage Metrics dashboard


