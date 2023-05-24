import requests

def get_data():
  url = "https://apis.roblox.com/datastores/v1/universes/12426295363/standard-datastores"
  headers = {
      "x-api-key": "AxtnrO2MwkC+NdID7Il75IWCimQy+1PLp5zsZDYXR8bqTEuL"
  }
  request = requests.get(url, headers=headers)
  if request.status_code != 200:
    print(request.status_code)
    return
  
  data = request.json()
  print(data)

get_data()