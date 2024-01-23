
import pandas as pd
import msal
import requests

# Enter the details of your AAD app registration
client_id = 'b2fa56e6-592b-4cd6-842d-7984d8a16d94'
client_secret = 'plh8Q~EPFGH5iVLa_Zb9yt4tgnbVPlJ-H-K15c6k'

#https://login.microsoftonline.com/8ed8a585-d8e6-4b00-b9cc-d370783559f6/oauth2/v2.0/token HTTP/1.1
authority = 'https://login.microsoftonline.com/8ed8a585-d8e6-4b00-b9cc-d370783559f6'
scope = ['https://graph.microsoft.com/.default']

# Create an MSAL instance providing the client_id, authority and client_credential parameters
client = msal.ConfidentialClientApplication(client_id, authority=authority, client_credential=client_secret)

# First, try to lookup an access token in cache
token_result = client.acquire_token_silent(scope, account=None)

# If the token is available in cache, save it to a variable
if token_result:
  access_token = 'Bearer ' + token_result['access_token']
  print('Access token was loaded from cache')

# If the token is not available in cache, acquire a new one from Azure AD and save it to a variable
if not token_result:
  token_result = client.acquire_token_for_client(scopes=scope)
  access_token = 'Bearer ' + token_result['access_token']
  print('New access token was acquired from Azure AD')

print(access_token)

headers = {
  'Authorization': access_token
}

# Works
url = 'https://graph.microsoft.com/v1.0/users'
url = 'https://graph.microsoft.com/v1.0/sites/root/'


# Don't work
url = 'https://graph.microsoft.com/v1.0/applications/b2fa56e6-592b-4cd6-842d-7984d8a16d94'
url = 'https://graph.microsoft.com/v1.0/applications/'

url = 'https://graph.microsoft.com/v1.0/users/acazan@rmi.org/activities/recent'
url = 'https://graph.microsoft.com/v1.0/users/acazan@rmi.org/insights/used'
url = 'https://graph.microsoft.com/v1.0/users/ghoffman@rmi.org/insights/used'

url = 'https://graph.microsoft.com/v1.0/sites/getAllSites'

# Test site
url = 'https://graph.microsoft.com/v1.0/sites/rockmtnins.sharepoint.com,580daf44-9c0f-41e8-bfad-65feb351ba9b,5688865f-94e8-4383-b4be-3fa424fd62a1/pages'

#test site pages, works
url = 'https://graph.microsoft.com/beta/sites/rockmtnins.sharepoint.com,580daf44-9c0f-41e8-bfad-65feb351ba9b,5688865f-94e8-4383-b4be-3fa424fd62a1/pages'

# IT site details, works
url = 'https://graph.microsoft.com/v1.0/sites/rockmtnins.sharepoint.com,1e4669c5-f85e-4f92-ae01-dea9502981ee,a75e7be0-f434-4675-bdbc-6711c60735cb'

# It pages, Item not found
url = 'https://graph.microsoft.com/beta/sites/rockmtnins.sharepoint.com,1e4669c5-f85e-4f92-ae01-dea9502981ee,a75e7be0-f434-4675-bdbc-6711c60735cb/pages'
 

url = 'https://graph.microsoft.com/beta/sites/rockmtnins.sharepoint.com,1929b6b2-0c49-4caa-80e1-fa0e487ed950,4569ce04-0794-4df5-b00c-71f13bb60ce0/pages'

url = 'https://graph.microsoft.com/beta/sites/rockmtnins.sharepoint.com,1929b6b2-0c49-4caa-80e1-fa0e487ed950,4569ce04-0794-4df5-b00c-71f13bb60ce0'

# Make a GET request to the provided url, passing the access token in a header
graph_result = requests.get(url=url, headers=headers)

# Print the results in a JSON format
print(graph_result.json())

print(graph_result.meta)
df = pd.json_normalize(graph_result)

print(df.columns)