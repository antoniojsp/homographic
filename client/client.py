from phe import paillier
import json
from flask import request, url_for
from flask_api import FlaskAPI, status, exceptions
from flask import send_from_directory
from flask_cors import CORS
import requests
import logging
import os


app = FlaskAPI(__name__)
cors = CORS(app, resources={r'/*': {"origins": '*'}})

'''
Client encrypts the ballot
'''
def encrypt(public, input):
    encrynumber_list = [public.encrypt(x) for x in input]
    enc_temp = {}
    enc_temp['public_key'] = {'g': public.g, 'n': public.n}
    enc_temp['values'] = [(str(x.ciphertext()), x.exponent) for x in encrynumber_list]
    return json.dumps(enc_temp)

@app.route("/", methods=['GET','POST'])
def process():

  if (request.method == 'POST'):
    data = request.json
    if data:
        vote_list = [0,0,0,0]#representation of a ballot. Each index represent a cadidate. We enforce one vote per ballot by using droplist in the frontend
        vote_list[int(data['input'])] = 1 #add 1 to the index number of the candidate choosen
        key = requests.post('http://server_decrypt:90/key') #request a public key from the server to encrypt the ballot
        llave  = json.loads(key.text) #gets public key from the server_encrypt for encryptation 

        public_key_rec = paillier.PaillierPublicKey(n=int(llave['public_key']['n']))#create public key obj from the key sent by the server

        vote_encrypt_list = encrypt(public_key_rec, vote_list)#function encrypt the ballot. For instance, an list [0,1,0,0] means one vote for candidate 1
        temp = requests.post('http://server',json=vote_encrypt_list) #send data to the server to be added to the tally. Data is already encrypted encrypted.

        results = json.loads(temp.text) #gets sucess or fail, depents on the results of the vote counting 

        confirmation = json.dumps(results)
        app.logger.info(confirmation)
        return confirmation


@app.route("/css/<path:filename>")
def send_file(filename):
    return send_from_directory('css', filename)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
