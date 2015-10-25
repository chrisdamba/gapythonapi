"""This application demonstrates a use case with tasks on Working with AppBoy API using Python.

# predefinition1: Users already exist in the Appboy account and we are only interested in
updating existing values.

# predefinition2: The max of user objects per API call is 50.

# predefinition3: Given tables below
User table contains one entry per user
CREATE TABLE appboy.user
(
  user_external_id text, unique
  identifier for this user.
  email text, email
  address for the user.
  optin_status integer, indicates
  the user's optin
  status.
  app_group_id text, the
  appboy app_group to which this user belongs.
  first_name text,
  last_name text,
  user_zipcode text,
  user_city text,
  last_modified_at timestamp
)

User events contains multiple events per user.
CREATE TABLE appboy.user_events
(
  user_events_id bigint, Unique
  row identifier for this table.
  user_id integer, Identifier
  for this user FK
  for the user table.
  name character varying, The
  name of the event (not the user!) E.g: user click, user email opening.
  time timestamp with time zone The time of the event.
);

Sample Application Usage:

  $ python AppBoyApi.py

"""

import requests
import datetime
import time

def get_users_response_object(request_url, app_group_id):
  """Gets the json response for a given api request.

  Args:
    request_url: string The request API endpoint.
    app_group_id: string App Group Identifier.    

  Returns:
    A dictionary of the JSON response.
  """
  # Define the content type as a dictionary
  headers_params = {'Content-Type':'application/json'}


  # Store the request data as a dictionary
  data = {'app_group_id': app_group_id}

  # Do the HTTP get request
  response = requests.get(request_url, data=data, headers=headers_params)

  # Check for HTTP codes other than 200
  if response.status_code != 200:
      print('Status:', response.status_code, 'Problem with the request. Exiting.')
      exit()

  # Decode the JSON response into a dictionary and return the data
  data = response.json()

  # Return the data
  return data



def get_users_attributes(request_url, app_group_id):
  """Gets the Attribute objects of all the existing users in a list.

  Args:
    request_url: string The request API endpoint.
    app_group_id: string App Group Identifier.    

  Returns:
    A list of dictionaries with all the users Attribute objects.
  """  

  # Decode the JSON response into a dictionary and use the data
  data = get_users_response_object(request_url, app_group_id)

  # Return list of all the users attributes and values
  return data['attributes']

def get_users_events(request_url, app_group_id):
  """Gets the Event objects of all the existing users in a list.

  Args:
    request_url: string The request API endpoint.
    app_group_id: string App Group Identifier.    

  Returns:
    A list of dictionaries with all the users Event objects.
  """  

  # Decode the JSON response into a dictionary and use the data
  data = get_users_response_object(request_url, app_group_id)

  # Return list of all the users attributes and values
  return data['events']

def update_user(request_url, app_group_id, data):
  """Updates the user data.

  Args:
    request_url: string The request API endpoint.
    app_group_id: string App Group Identifier.    

  Returns:
    A the JSON response of the put request.
  """
  # Define the content type as a dictionary
  headers_params = {'Content-Type':'application/json'}


  # Store the request data as a dictionary
  data['app_group_id']=app_group_id

  # Do the HTTP get request
  response = requests.post(request_url, data=data, headers=headers_params)

  # Check for HTTP codes other than 200
  if response.status_code != 200:
      print('Status:', response.status_code, 'Problem with the request. Exiting.')
      exit()  

  # Return the response 
  return response


def update_attribute_data(request_url, app_group_id, field, value):
  """Updates an existing user Attribute object field with the given value.

  Args:
    request_url: string The request API endpoint.
    app_group_id: string App Group Identifier.  
    field: str The user data attribute field to be updated.
    value: The new value to be updated.
  """
  
  attributes = get_users_attributes(request_url, app_group_id)
  data = []
  for user in attributes:    
    user[field]=value
    data.append(user)
      
  # The max of user objects per API call is 50 so split the data array into event chunks of 50
  for i in xrange(0, len(data), 50):
    yield data[i:i+n]
    update = { 'attributes': data }
    res = update_user(request_url, app_group_id, update)
    print res.text
    print res.status_code

def update_event_data(request_url, app_group_id, field, value):
  """Updates an existing user Event object field with the given value.

  Args:
    request_url: string The request API endpoint.
    app_group_id: string App Group Identifier.  
    field: str The user data Event object field to be updated.
    value: The new value to be updated.
  """
  
  events = get_users_events(request_url, app_group_id)
  data = []
  for user in events:    
    user[field]=value
    data.append(user)
  
  # The max of user objects per API call is 50 so split the data array into event chunks of 50
  for i in xrange(0, len(data), 50):
    yield data[i:i+n]
    update = { 'events': data }
    res = update_user_attributes(request_url, app_group_id, update)
    print res.text
    print res.status_code


def main():
  # Define the request endpoint.
  request_url = 'https://api.appboy.com/users/track'

  # App Group Identifier.
  app_group_id = '38a46418-0026-4b7b-8931-41cd5224ac07'
  
  # TaskA1: Update user attributes and user event data on an AppBoy account for all users in the tables!
  update_attribute_data(request_url, app_group_id, 'last_modified_at', datetime.datetime.utcnow())
  update_event_data(request_url, app_group_id, 'time', time.time())
  
if __name__ == '__main__':
  main()
