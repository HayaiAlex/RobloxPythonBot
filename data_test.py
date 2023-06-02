import requests
id = 4371347484
def get_data():
  url = f"https://apis.roblox.com/datastores/v1/universes/{id}/standard-datastores"
  headers = {
      "x-api-key": "AxtnrO2MwkC+NdID7Il75IWCimQy+1PLp5zsZDYXR8bqTEuL"
  }
  request = requests.get(url, headers=headers)
  if request.status_code != 200:
    print(request.status_code)
    return
  
  data = request.json()
  # print(data)

# get_data()

def get_ordered_datastore_stat(user, unverse_id, datastore_name):
    url = f"https://apis.roblox.com/ordered-data-stores/v1/universes/{unverse_id}/orderedDataStores/{datastore_name}/scopes/global/entries/{user}"
    try:
      request = requests.get(
        url,
        headers={'x-api-key': 'AxtnrO2MwkC+NdID7Il75IWCimQy+1PLp5zsZDYXR8bqTEuL'})
      print(request)
      response = request.json()
      print(response)
      if response.get('data'):
          return response['data']['value']
      else:
          return None
    except:
      return None
print(get_ordered_datastore_stat(74851095, 4371347484, 'Solos'))


def get_ordered_data(orderedDataStore):
  def get_page(orderedDataStore, page=None):
    url = f"https://apis.roblox.com/ordered-data-stores/v1/universes/{id}/orderedDataStores/{orderedDataStore}/scopes/global/entries?max_page_size=100"
    headers = {
        "x-api-key": "AxtnrO2MwkC+NdID7Il75IWCimQy+1PLp5zsZDYXR8bqTEuL"
    }
    request = requests.get(url, headers=headers)
    print(request.status_code)
    if request.status_code != 200:
      return
    
    data = request.json()
    return data

  data = get_page(orderedDataStore)
  # data += get_page(orderedDataStore, data['nextPageToken'])
  print(data)
  # for row in data['entries']:
  #   print(f"{row['value']} kills by {row['id']}")
get_ordered_data('Duos')


# Ordered Datastores
# Solos
# Duos

# SwordsKills
# SwordsWins
# SwordsKD

# GunsKills
# GunsWins
# GunsKD

# Datastores
# SwordsDeaths
# GunsDeaths