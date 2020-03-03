import json
import requests
import random
import time
from graph import graph as graph
# from decouple import config
# SECRET_KEY = config('SECRET_KEY')
token = "41b8bab923e9ecc5b7c6685ef794e68d2860ae28"
# graph = 
# 59,60
# n + 0 1
# s - 0,1
# w - 1,0
# e + 1,0
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
url = 'https://lambda-treasure-hunt.herokuapp.com/api/adv/init/'
current = requests.get(url, headers={'Authorization': f'Token {token}'}).json()
if current['room_id'] not in graph:
  new_room = {}
  for direction in current['exits']:
      new_room[direction] = "?"
  graph[current['room_id']] = [new_room, current]


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
# bfs(current['room_id'], 492)
# Treasure
def take_item(treasure):
  url = 'https://lambda-treasure-hunt.herokuapp.com/api/adv/take/'
  time.sleep(current['cooldown'])
  data = f'{{"name":"{treasure}"}}'
  result = requests.post(url, data=data,
                         headers={'Content-Type':'application/json',
                                  'Authorization': f'Token {token}'}).json()
  if result['errors'] == ['Item not found: +5s CD']:
    print(result['errors'])
  else:
    print(f'Taking {treasure}!')
  return result
# Selling Treasure
def sell_item(treasure):
  url = 'https://lambda-treasure-hunt.herokuapp.com/api/adv/sell/'
  data = f'{{"name":"{treasure}", "confirm":"yes"}}'
  result = requests.post(url, data=data,
                         headers={'Content-Type':'application/json',
                                  'Authorization': f'Token {token}'}).json()
  time.sleep(current['cooldown'])
  print(f'Selling {treasure} to shop.\n{result}')
  return result
def status_check():
  url = 'https://lambda-treasure-hunt.herokuapp.com/api/adv/status/'
  result = requests.post(url, headers={'Content-Type':'application/json',
                                       'Authorization': f'Token {token}'})
  print(result.json())
  time.sleep(current['cooldown'])
  return result.json()
# status_check()

def movement(direction, next_room_id=None):
  if graph[current['room_id']][1]['terrain'] == 'CAVE':
    url = 'https://lambda-treasure-hunt.herokuapp.com/api/adv/move/'
  else:
    url = 'https://lambda-treasure-hunt.herokuapp.com/api/adv/fly/'
  if next_room_id is not None:
    data = f'{{"direction":"{direction}","next_room_id": "{next_room_id}"}}'
    if graph[next_room_id][1]['terrain'] == 'CAVE':
      url = 'https://lambda-treasure-hunt.herokuapp.com/api/adv/move/'
  else:
    data = f'{{"direction":"{direction}"}}'
  
  result = requests.post(url, data=data,
                         headers={'Content-Type':'application/json',
                                  'Authorization': f'Token {token}'}).json()
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
  graph[current['room_id']][0][direction] = result['room_id']
  graph[result['room_id']][0][inverse_directions[direction]] = current['room_id']
  print(result)
  return result
inverse_directions = {"n": "s", "s": "n", "e": "w", "w": "e"}
# prev_move = None
while True:
    current_exits = graph[current['room_id']][0]
    # if status_check()['encumbrance'] > 0:
      # If inventory getting too full, go sell at shop
    # print(bfs(current['room_id'], 1))
    # target = bfs(current['room_id'], 1)
    # print('Heading to shop..')
    # for direction, room_id in current_exits.items():
    #   if room_id == target:
    #     next_move = direction
    #     print("You are at the shop")
    #     break
    # if status_check()['gold'] >= 1000:
    #   # Change name to get clue for Lambda coin
    # Wishing well = 55 , Shop = 1 **************************************************
    target = bfs(current['room_id'], 492)[1]
    print('Heading to Target..')
    for direction, room_id in current_exits.items():
      if room_id == target:
        next_move = direction
        break
    # else:
    # directions = []
    # for direction, room_id in current_exits.items():
    #     # If adjacent room_id not visited yet, add that direction
    #     if room_id == "?":
    #         directions.append(direction)
    # if len(directions) == 0:
    #     print('All adjacent rooms visited..')
    #     target = bfs(current['room_id'], "?")[1]
    #     for direction, room_id in current_exits.items():
    #         if room_id == target:
    #             next_move = direction
    #             break
    #     directions = [direction for direction in current_exits.keys()]
    #     if len(directions) == 1:
    #         next_move = directions[0]
    #     else:
    #         if prev_move is not None:
    #             directions.remove(inverse_directions[prev_move])
    #         next_move = random.choice(directions)
    # else:
    #     next_move = random.choice(directions)
    # print(f'Next room: {current_exits[next_move]}')
    print(f'Room[{current["room_id"]}] to Room[{current_exits[next_move]}]')
    if current_exits[next_move] == "?":
      print(f"Traveling to the unknown.. ({len(graph)}/500)")
      end_room = movement(next_move)
    else:
      # Use "Wise Explorer" buff
      time.sleep(current['cooldown'])
      end_room = movement(next_move, current_exits[next_move])
    print(f"CD: {end_room['cooldown']}, {end_room['messages']}")
    # if len(end_room['items']) > 0:
    #   for item in end_room['items']:
    #     if 'treasure' not in item:
    #       print(f'{item} found in {end_room["room_id"]}')
    #       time.sleep(end_room['cooldown'])
    #       end_room = take_item(item)
    if end_room['title'] == 'Shop':
      time.sleep(end_room['cooldown'])
      items = status_check()['inventory']
      for item in items:
        if 'treasure' in item:
          time.sleep(end_room['cooldown'])
          end_room = sell_item(item)
    prev_move = next_move
    current = end_room
    time.sleep(current['cooldown'])
    # if current_exits[next_move] == "?":
    #     print(f"TEST-- Traveling to the unknown.. ({len(graph)}/500)")
    #     end_room = movement(next_move)
    # else:
    #     # Use "Wise Explorer" buff
    #     print(f'Obtaining "Wise Explorer" buff..')
    #     end_room = movement(next_move, current_exits[next_move])
    # print("end_room: ",end_room)
    # if len(end_room['items']) > 0:
    #     for item in end_room['items']:
    #         print(f'{item} found in {end_room["room_id"]}')
    #     if 'treasure' not in item:
    #         time.sleep(end_room['cooldown'])
    #         end_room = take_item(item)
    # # if 'Shrine' in end_room['title']:
    # #   time.sleep(end_room['cooldown'])
    # #   pray()
    # # elif end_room['title'] == 'Shop':
    # #   time.sleep(end_room['cooldown'])
    # #   items = status_check()['inventory']
    # #   for item in items:
    # #     if 'treasure' in item:
    # #       time.sleep(end_room['cooldown'])
    # #       end_room = sell_item(item)
    # prev_move = next_move
    # current = end_room
    # time.sleep(current['cooldown'])