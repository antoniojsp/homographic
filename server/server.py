from phe import paillier
import json
from random import *
from flask import request, url_for
from flask_api import FlaskAPI, status, exceptions
import pymongo # modules
from pymongo import MongoClient
import os
import requests

'''
server.py connects with client.py and gets the encrypted ballot and perform the addition of the vote into the tally. It gets the public key from server_decrypt.py and does not handle the private key since we don't want to have the chance of having both keys in the same location in this server since there is sensitive data.
'''

app = FlaskAPI(__name__)


'''
Connects with atlas db to stores values
'''
client = MongoClient("mongodb+srv://antonio:antonio@cluster0.hb8y0.mongodb.net/experiment?retryWrites=true&w=majority", ssl=True,ssl_cert_reqs='CERT_NONE')
db = client.election  # create database
collection = db.vote
number_votes =  db.number


'''
add_vote(tally_encrypt:list, vote_received_encrypt:list) function
    tally_encrypt => current total tally encrypted extracted from mongodb
    vote_received_encrypt => ballot with one elector vote (encrypted)

it add up the values from the current tally with the ballot. A ballot has values from 0 to 1, 1 represents the candidate election (depends on the index). All the information is encrypted and uses the properties of homorphic encryption to perform addition.
'''



def add_vote(tally_encrypt:list, vote_received_encrypt:list):#send public key to the client to encrypt the ballot

    for i in range(len(tally_encrypt)): #perform an addition bewtween the value in the tally and the value in the vote (same position indicates same candidate)
        tally_encrypt[i]+= vote_received_encrypt[i]

'''
Handles the process to add a vote to the tally

A ballot is recorded by the client in the form of a list, I.E [0,0,0,1], this example means that the fourth candidate has been selected. The client encrypt the values of this array and send it to the server. The properties of homomorphic encryption allows perform additions and multiplications without decrypting the information. We perform the addition here and then transform the EncryptedNumber objects into ciphertext to be stored in mongodb.
'''
@app.route("/", methods=['POST'])
def process():
    
    if request.method == 'POST':

        vote_encrypted = json.loads(request.data) # gets the encrypted ballots from the client
        try: # in case of failure, returns an output with the message "Failure", otherwise, "Success"
            
            key = requests.post('http://server_decrypt:90/key') #request a public key from the server_encrypt to encrypt the ballot
            llave  = json.loads(key.text) #gets public key from the server for encryptation 
            public_key_rec = paillier.PaillierPublicKey(n=int(llave['public_key']['n']))#create public key obj from the key sent by the server

            vote_received_enc = [paillier.EncryptedNumber(public_key_rec, int(x[0]), int(x[1])) for x in vote_encrypted['values']] # convert the cipher values received front the frontend in EncryptedNumber objects

            tally_mongo_encrypted = [i for i in collection.find()][0]["votes"]

            encriptado_temp = [paillier.EncryptedNumber(public_key_rec, int(j)) for j in tally_mongo_encrypted] # gets the current tally values that are record in the db. Convert those values in EncryptedNumber objects.

            add_vote(encriptado_temp, vote_received_enc) # add the ballot to the tally
            cipher_values = [str(i.ciphertext()) for i in encriptado_temp] # creates list with the ciphertext to be stored in mongodb

            collection.delete_many({})
            collection.insert_one({"id_votes":"nuevo" , "votes":cipher_values}) # insert value to

            temp = {}
            temp['output'] = "Success!" # confirmation

        except:
            temp = {}
            temp['output'] = "Failure!" # confirmation

        results = json.dumps(temp)
        return results

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
