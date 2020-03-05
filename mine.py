import json
import time
import random
import requests

token = "41b8bab923e9ecc5b7c6685ef794e68d2860ae28"


url = 'https://lambda-treasure-hunt.herokuapp.com/api/adv/init/'
current = requests.get(url, headers={'Authorization': f'Token {token}'}).json()

## Mining Coin

def get_last_proof():

  url = 'https://lambda-treasure-hunt.herokuapp.com/api/bc/last_proof/'
  result = requests.get(url, 
                        headers={'Content-Type':'application/json',
                                 'Authorization': f'Token {token}'}).json()
  return result
# get_last_proof()

def proof_of_work(last_proof, current_level):
    """
    Get the last valid proof to use to mine a new block. 
    Also returns the current difficulty level, which is the number of 0's 
    required at the beginning of the hash for a new proof to be valid.
    The proof of work algorithm for this blockchain is 
    not the same as we used in class.
    """
    start = timer()
    print(f"\nLast proof: {last_proof} -- Searching for next proof..\n")
    proof = 1000000
    while valid_proof(last_proof, proof, current_level) is False:
      proof += 1
    print(f"Proof found: {proof} in {timer() - start:.3f}s")
    return proof

import hashlib
def valid_proof(last_proof, proof, current_level):
    """
    Does hash(last_proof, proof) contain N leading zeroes, 
    where N is the current difficulty level?
    Use sha256 in hashlib
    """
    guess = f"{last_proof}{proof}".encode()
    guess_hash = hashlib.sha256(guess).hexdigest()

    return guess_hash[:current_level] == "0"*current_level

def mine_coin(new_proof):
  url = 'https://lambda-treasure-hunt.herokuapp.com/api/bc/mine/'
  data = f'{{"proof":{new_proof}}}'
  result = requests.post(url, data=data,
                         headers={'Content-Type':'application/json',
                                  'Authorization': f'Token {token}'}).json()
  return result

from timeit import default_timer as timer
# Run forever until interrupted
while True:
  # Get the last proof from the server
  time.sleep(current['cooldown'])
  current_proof = get_last_proof()
  print(current_proof)
  time.sleep(current['cooldown'])
  proof = current_proof['proof']
  current_level = current_proof['difficulty']

  new_proof = proof_of_work(proof, current_level)
  response = mine_coin(new_proof)
  print(response)
  time.sleep(response['cooldown'])
  if (response['messages'] == ['New Block Forged']):
    break