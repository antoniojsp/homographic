from phe import paillier
import json
from random import *
from flask import request, url_for
from flask_api import FlaskAPI, status, exceptions
import pymongo # modules
from pymongo import MongoClient
import os


app = FlaskAPI(__name__)

'''
Connects with atlas db to stores values
'''

client = MongoClient("mongodb+srv://antonio:antonio@cluster0.hb8y0.mongodb.net/experiment?retryWrites=true&w=majority", ssl=True,ssl_cert_reqs='CERT_NONE')
db = client.election  # create database or connect
collection = db.vote
number_votes =  db.number

public_key_server, private_key_server = paillier.generate_paillier_keypair()#keys from the server. We send the public key to the client to encrypt the ballot and also to the server to perform the calculations necessary. We keep the private key here to perform the decryption to get the results

'''
Send a the public key to the client so it can encrypt the vote to be transmited to the server securely
'''
@app.route("/key", methods=['POST'])
def key():#send public key to the client to encrypt the ballot
    if request.method == 'POST':
        key = {}
        key['public_key'] = {'g': public_key_server.g, 'n': public_key_server.n} # values necessary to create a public key object in the client
        return json.dumps(key)

@app.route("/results", methods=['POST'])
def results():

    if request.method == 'POST':
        results = [ paillier.EncryptedNumber(public_key_server, int(j))for j in [i for i in collection.find()][0]["votes"]] # gets encrypted results

        temp = {}
        temp['output'] = [private_key_server.decrypt(x) for x in results]  # decrypt values to be shown.
        app.logger.info(temp)

        return json.dumps(temp)

@app.route("/new", methods=['POST'])
def new():
    if request.method == 'POST':
        nuevo = [str(public_key_server.encrypt(0).ciphertext()) for i in range(0,4)]#list lenght number of candidates
        collection.update_one({"id_votes":"nuevo"}, {"$set": {"votes":nuevo}})
        return

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=90, debug=True)
