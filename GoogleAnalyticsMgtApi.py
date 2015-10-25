"""This application demonstrates a use case with tasks on Working with Google Analytics Management API using Python.

# predefinition1: You must have signed up for a new project in the Google APIs console:
https://code.google.com/apis/console

# predefinition2: You must have registered the project to use OAuth2.0 for installed applications as this requires authorization with at least one of the following scopes:
https://www.googleapis.com/auth/analytics.edit
https://www.googleapis.com/auth/analytics.readonly

# predefinition3: Add the client id, client secret, and redirect URL into the client_secrets.json file that is in the same directory as this sample.

# predefinition4: API Client Library for Python is installed. The Google API Client Library for Python is designed for Python client-application developers. 
It offers simple, flexible access to many Google APIs.

Install the library using standard Python tools, and there are custom installs optimized for Google App Engine:

 $ pip install --upgrade google-api-python-client

Sample Application Usage:

  $ python GoogleAnalyticsMgtApi.py

"""

import argparse

from apiclient.discovery import build
import httplib2
from oauth2client import client
from oauth2client import file
from oauth2client import tools
from urllib2 import HTTPError


def get_service(api_name, api_version, scope, client_secrets_path):
  """Get a service that communicates to a Google API.

  Args:
    api_name: string The name of the api to connect to.
    api_version: string The api version to connect to.
    scope: A list of strings representing the auth scopes to authorize for the
      connection.
    client_secrets_path: string A path to a valid client secrets file.

  Returns:
    A service that is connected to the specified API.
  """
  # Parse command-line arguments.
  parser = argparse.ArgumentParser(
      formatter_class=argparse.RawDescriptionHelpFormatter,
      parents=[tools.argparser])
  flags = parser.parse_args([])

  # Set up a Flow object to be used if we need to authenticate.
  flow = client.flow_from_clientsecrets(
      client_secrets_path, scope=scope,
      message=tools.message_if_missing(client_secrets_path))

  # Prepare credentials, and authorize HTTP object with them.
  # If the credentials don't exist or are invalid run through the native client
  # flow. The Storage object will ensure that if successful the good
  # credentials will get written back to a file.
  storage = file.Storage(api_name + '.dat')
  credentials = storage.get()
  if credentials is None or credentials.invalid:
    credentials = tools.run_flow(flow, storage, flags)
  http = credentials.authorize(http=httplib2.Http())

  # Build the service object.
  service = build(api_name, api_version, http=http)

  return service


def create_dimension(service, account_id, web_property_id, name, scope, active=True):
  """Creates a new custom dimension.

  Args:
    service: The service object built by the Google API Python client library.
    account_id: str The Account ID for the custom dimension to update.
    web_property_id: str The Web property ID for the custom dimension to create.
    name: str The name of the custom dimension.
    scope: str The scope of the custom dimension: HIT, SESSION, USER or PRODUCT.
    active: bool Boolean indicating whether the custom dimension is active. Default value is True.
  """
  try:
    dimension_body={
      'name': name,
      'scope': scope,
      'active': active
    }   
    service.management().customDimensions().insert(
      accountId=account_id,
      webPropertyId=web_property_id,
      body=dimension_body
    ).execute()

  except TypeError, error:
    # Handle errors in constructing a query.
    print 'There was an error in constructing your query : %s' % error

  except HTTPError, error:
    # Handle API errors.
    print ('There was an API error : %s : %s' %
           (error.resp.status, error.resp.reason))

def create_dimensions(service, account_id, web_property_id):
  """Creates 10 custom session dimensions ('dimension1'...'dimension10').

  Args:
    service: The service object built by the Google API Python client library.
    account_id: str The Account ID for the custom dimension to update.
    web_property_id: str The Web property ID for the custom dimension to create.    
  """
  for i in range(1, 11):
    name = 'dimension'+str(i)   
    create_dimension(service, account_id, web_property_id, name, 'SESSION')

def update_dimension(service, account_id, web_property_id, dimension_id, field, value):
  """Updates an existing custom dimension field with the given value.

  Args:
    service: The service object built by the Google API Python client library.
    account_id: str The Account ID for the custom dimension to update.
    web_property_id: str The Web property ID for the custom dimension to update.
    field: str The custom dimension field to be updated.
    value: The new value to be updated.
  """
  update_body={}
  update_body[field]=value
  try:
    service.management().customDimensions().update(
      accountId=account_id,
      webPropertyId=web_property_id,
      customDimensionId=dimension_id,
      body=update_body).execute()

  except TypeError, error:
    # Handle errors in constructing a query.
    print 'There was an error in constructing your query : %s' % error

  except HttpError, error:
    # Handle API errors.
    print ('There was an API error : %s : %s' %
           (error.resp.status, error.resp.reason))    

def update_dimensions_name(service, account_id, web_property_id):
  """Updates an existing custom dimension name. Changes the name of 'dimension1'...'dimension5' to 'dimensionA'...'dimensionE'!

  Args:
    service: The service object built by the Google API Python client library.
    account_id: str The Account ID for the custom dimension to update.
    web_property_id: str The Web property ID for the custom dimension to update.
  """
  for i in range(1, 6):
    dimension_id='ga:dimension' + str(i)
    new_name='dimension' + chr(i + ord('A'))
    update_dimension(service, account_id, web_property_id, dimension_id, 'name', new_name)

def update_dimensions_scope(service, account_id, web_property_id):
  """Updates an existing custom dimension scope. Changes the scope of 'dimension6'...'dimension10' to a PRODUCT.

  Args:
    service: The service object built by the Google API Python client library.
    account_id: str The Account ID for the custom dimension to update.
    web_property_id: str The Web property ID for the custom dimension to update.
  """
  for i in range(6, 11):
    dimension_id='ga:dimension'+str(i)    
    update_dimension(service, account_id, web_property_id, dimension_id, 'scope', 'PRODUCT')

def print_results(service):
  """Traverses the management API hiearchy and prints results.

  This retrieves and prints the authorized user's accounts,
  retrieves and prints all the web properties for the first account,
  retrieves and prints all the views (profiles) for the first web property of the user's account.

  Args:
    service: The service object built by the Google API Python client library.

  Raises:
    HttpError: If an error occured when accessing the API.
    AccessTokenRefreshError: If the current token was invalid.
  """

  accounts = service.management().accounts().list().execute()
  print_accounts(accounts)

  if accounts.get('items'):
    firstAccountId = accounts.get('items')[0].get('id')
    webproperties = service.management().webproperties().list(
        accountId=firstAccountId).execute()

    print_webproperties(webproperties)

    if webproperties.get('items'):
      firstWebpropertyId = webproperties.get('items')[0].get('id')
      profiles = service.management().profiles().list(
          accountId=firstAccountId,
          webPropertyId=firstWebpropertyId).execute()

      print_profiles(profiles)

  print_segments(service.management().segments().list().execute())


def print_accounts(accounts_response):
  """Prints all the account info in the Accounts Collection.

  Args:
    accounts_response: The response object returned from querying the Accounts
        collection.
  """

  print '------ Account Collection -------'
  print_pagination_info(accounts_response)
  print

  for account in accounts_response.get('items', []):
    print 'Account ID      = %s' % account.get('id')
    print 'Kind            = %s' % account.get('kind')
    print 'Self Link       = %s' % account.get('selfLink')
    print 'Account Name    = %s' % account.get('name')
    print 'Created         = %s' % account.get('created')
    print 'Updated         = %s' % account.get('updated')

    child_link = account.get('childLink')
    print 'Child link href = %s' % child_link.get('href')
    print 'Child link type = %s' % child_link.get('type')
    print

  if not accounts_response.get('items'):
    print 'No accounts found.\n'


def print_webproperties(webproperties_response):
  """Prints all the web property info in the WebProperties collection.

  Args:
    webproperties_response: The response object returned from querying the
        Webproperties collection.
  """

  print '------ Web Properties Collection -------'
  print_pagination_info(webproperties_response)
  print

  for webproperty in webproperties_response.get('items', []):
    print 'Kind               = %s' % webproperty.get('kind')
    print 'Account ID         = %s' % webproperty.get('accountId')
    print 'Web Property ID    = %s' % webproperty.get('id')
    print ('Internal Web Property ID = %s' %
           webproperty.get('internalWebPropertyId'))

    print 'Website URL        = %s' % webproperty.get('websiteUrl')
    print 'Created            = %s' % webproperty.get('created')
    print 'Updated            = %s' % webproperty.get('updated')

    print 'Self Link          = %s' % webproperty.get('selfLink')
    parent_link = webproperty.get('parentLink')
    print 'Parent link href   = %s' % parent_link.get('href')
    print 'Parent link type   = %s' % parent_link.get('type')
    child_link = webproperty.get('childLink')
    print 'Child link href    = %s' % child_link.get('href')
    print 'Child link type    = %s' % child_link.get('type')
    print

  if not webproperties_response.get('items'):
    print 'No webproperties found.\n'


def print_profiles(profiles_response):
  """Prints all the profile info in the Profiles Collection.

  Args:
    profiles_response: The response object returned from querying the
        Profiles collection.
  """

  print '------ Profiles Collection -------'
  print_pagination_info(profiles_response)
  print

  for profile in profiles_response.get('items', []):
    print 'Kind                      = %s' % profile.get('kind')
    print 'Account ID                = %s' % profile.get('accountId')
    print 'Web Property ID           = %s' % profile.get('webPropertyId')
    print ('Internal Web Property ID = %s' %
           profile.get('internalWebPropertyId'))
    print 'Profile ID                = %s' % profile.get('id')
    print 'Profile Name              = %s' % profile.get('name')

    print 'Currency         = %s' % profile.get('currency')
    print 'Timezone         = %s' % profile.get('timezone')
    print 'Default Page     = %s' % profile.get('defaultPage')

    print ('Exclude Query Parameters        = %s' %
           profile.get('excludeQueryParameters'))
    print ('Site Search Category Parameters = %s' %
           profile.get('siteSearchCategoryParameters'))
    print ('Site Search Query Parameters    = %s' %
           profile.get('siteSearchQueryParameters'))

    print 'Created          = %s' % profile.get('created')
    print 'Updated          = %s' % profile.get('updated')

    print 'Self Link        = %s' % profile.get('selfLink')
    parent_link = profile.get('parentLink')
    print 'Parent link href = %s' % parent_link.get('href')
    print 'Parent link type = %s' % parent_link.get('type')
    child_link = profile.get('childLink')
    print 'Child link href  = %s' % child_link.get('href')
    print 'Child link type  = %s' % child_link.get('type')
    print

  if not profiles_response.get('items'):
    print 'No profiles found.\n'


def print_pagination_info(results):
  """Prints common pagination details.

  Args:
    results: The response returned from the Core Reporting API.
  """

  print 'Pagination Infos:'
  print 'Items per page = %s' % results.get('itemsPerPage')
  print 'Total Results  = %s' % results.get('totalResults')

  # These only have values if other result pages exist.
  if results.get('previousLink'):
    print 'Previous Link  = %s' % results.get('previousLink')
  if results.get('nextLink'):
    print 'Next Link      = %s' % results.get('nextLink')
  print



def main():
  # Define the auth scopes to request.
  scope = ['https://www.googleapis.com/auth/analytics.readonly']

  # Authenticate and construct service.
  service = get_service('analytics', 'v3', scope, 'client_secrets.json')
  
  # Set up API headers
  # Account ID for the custom dimension to create/update.
  account_id = '123456'

  # Web property ID for the custom dimension to create/update
  web_property_id = 'UA-123456-1'
  
  # TaskA1: Create 10 custom session dimensions (‘dimension1’...’dimension10’)!
  create_dimensions(service, account_id, web_property_id)

  # TaskA2: Change the name of ‘dimension1’...’dimension5’ to ‘dimensionA’...’dimensionE’!
  update_dimensions_name(service, account_id, web_property_id)

  # TaskA3: Change the scope of ‘dimension6’…’dimension10’ to a different one!
  update_dimensions_scope(service, account_id, web_property_id)

  # TaskB1: Get all GA accounts, properties & views for a Google account of your choice and
  # provide/visualize an overview for it!
  print_results(service)
  
if __name__ == '__main__':
  main()
