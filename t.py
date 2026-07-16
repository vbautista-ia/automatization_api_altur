from datetime import datetime
import os
import time

import requests
from collections import defaultdict


TOKEN = 'api-key sk-y1WYihu7Tuezza2j7VUcQ73No1oM9b0HO'
AUTHORIZATION = {'Authorization': TOKEN}

response = requests.get('https://api.altur.io/api/v1.0/call/cll_UerEkCNKqEWM6iu28Mvo', headers=AUTHORIZATION)

result = response.json()
print(result)