import json
import requests
import random
import time
# from graph import graph

token = "41b8bab923e9ecc5b7c6685ef794e68d2860ae28"

class Queue:
    def __init__(self):
        self.queue = []
    def enqueue(self, value):
        self.queue.append(value)
    def dequeue(self):
        if self.size() > 0:
            return self.queue.pop(0)
        else:
            return None
    def size(self):
        return len(self.queue)
graph = {}
url = 'https://lambda-treasure-hunt.herokuapp.com/api/adv/init/'
current = requests.get(url, headers={'Authorization': f'Token {token}'}).json()
if current['room_id'] not in graph:
  new_room = {}
  for direction in current['exits']:
      new_room[direction] = "?"
  graph[current['room_id']] = [new_room, current]
# current

def init(token):
  url = 'https://lambda-treasure-hunt.herokuapp.com/api/adv/init/'
  result = requests.get(url, 
                         headers={'Authorization': f'Token {token}'}).json()
  if len(result['errors']) > 0:
    print(result['errors'])
  if result['room_id'] not in graph:
    new_room = {}
    for direction in result['exits']:
        new_room[direction] = "?"
    graph[result['room_id']] = [new_room, result]
  return result
# current = init(token)
# current

# # init(token)


def bfs(starting_room, destination):
  queue = Queue()
  queue.enqueue([starting_room])
  visited = set()
  while queue.size() > 0:
    path = queue.dequeue()
    room_id = path[-1]
    if room_id not in visited:
      if room_id == destination:
        return path
      else:
        for direction in graph[room_id][0]:
          if graph[room_id][0][direction] != "?":
            new_path = path.copy()
            new_path.append(graph[room_id][0][direction])
            queue.enqueue(new_path)
      visited.add(room_id)
  return []

# bfs(current['room_id'], 500)

# Movement
def movement(current_room_id, direction, next_room_id=None):
  if graph[current_room_id][1]['terrain'] == 'CAVE':
    url = 'https://lambda-treasure-hunt.herokuapp.com/api/adv/move/'
  else:
    # Once you acquire flying ability
    url = 'https://lambda-treasure-hunt.herokuapp.com/api/adv/fly/'
  if next_room_id is not None and next_room_id != "?":
    data = f'{{"direction":"{direction}","next_room_id": "{next_room_id}"}}'
    if graph[next_room_id][1]['terrain'] == 'CAVE':
      url = 'https://lambda-treasure-hunt.herokuapp.com/api/adv/move/'
  else:
    data = f'{{"direction":"{direction}"}}'
  
  result = requests.post(url, data=data,
                         headers={'Content-Type':'application/json',
                                  'Authorization': f'Token {token}'}).json()
  if len(result['errors']) > 0:
    print(result['errors'])
    return
  # Update room_id in graph
  inverse_directions = {"n": "s", "s": "n", "e": "w", "w": "e"}
  if result['room_id'] not in graph:
    graph[result['room_id']] = {}
    for road in result['exits']:
      graph[result['room_id']][road] = "?"
    new_room = {}
    for road in result['exits']:
      new_room[road] = "?"
    graph[result['room_id']] = [new_room, result]
  graph[current_room_id][0][direction] = result['room_id']
  graph[result['room_id']][0][inverse_directions[direction]] = current_room_id

  return result


current = init(token)
time.sleep(current['cooldown'])
# Run forever until interrupted
prev_move = None
inverse_directions = {"n": "s", "s": "n", "e": "w", "w": "e"}
while True:
  directions = current['exits']
  if len(directions) > 1 and prev_move:
    directions.remove(inverse_directions[prev_move])
  direction = random.choice(directions)
  print(current['room_id'], direction, graph[current['room_id']][0])
  next_room = movement(current['room_id'], direction, graph[current['room_id']][0][direction])
  print(current['room_id'], next_room['room_id'], next_room['messages'])
  time.sleep(next_room['cooldown'])

  quality = ['sparkling','brilliant','dazzling','spectacular','amazing','golden','well-crafted','exquisite']
  if len(next_room['items']) > 0:
    print(f'{next_room["items"]} found in Room[{next_room["room_id"]}]')
    for item in next_room['items']:          
      item_grade = item.split(' ')[0]
      if item_grade in quality:
        time.sleep(next_room['cooldown'])
        next_room = take_item(item)
  prev_move = direction
  current = next_room
  time.sleep(next_room['cooldown'])