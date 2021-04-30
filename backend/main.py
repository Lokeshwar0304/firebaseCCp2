import math
import os
import re
from flask import Flask, request, jsonify,render_template
from google.auth.transport import requests
from werkzeug.utils import  secure_filename
from firebase_admin import credentials, firestore, initialize_app, storage
from flask_cors import CORS, cross_origin
from math import radians, cos, sin, asin, sqrt, inf
from PIL import Image
from facenet_pytorch import MTCNN, InceptionResnetV1
import tensorflow as tf
import numpy as np
import pickle
import shutil

#pip install facenet-pytorch



app = Flask(__name__)
CORS(app)


base_path=os.getcwd();
UPLOAD_FOLDER = os.path.join(base_path, 'images')
TEMP_FOLDER = os.path.join(base_path, 'temp')

if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

if not os.path.isdir(TEMP_FOLDER):
    os.mkdir(TEMP_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TEMP_FOLDER'] = TEMP_FOLDER
ALLOWED_EXTENSIONS = set([ 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


cred = credentials.Certificate('key.json')
default_app = initialize_app(cred)
db = firestore.client()
bucket = storage.bucket('bloodbankasaservice.appspot.com')

firebase_request_adapter = requests.Request()

mtcnn = MTCNN()
resnet = InceptionResnetV1(pretrained='vggface2').eval()

users = db.collection('User')
log=db.collection('Log')
requests=db.collection('Requests')

@app.route('/upload', methods=['POST'])
@cross_origin()
def upload():
    try:
        if request.files:
            files = request.files.values()
            email = request.form['email']
            user = email.split('@')[0]
            current_path= os.path.join(app.config['UPLOAD_FOLDER'], user)
            if not os.path.isdir(current_path):
                os.mkdir(current_path)
            embeddings=[]
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(current_path, filename))
                    embeddings.append(create_embeddings(filename,current_path))
            
            if len(embeddings)>0:
                footprint = np.mean(embeddings) 
                docs = users.where(u'email', u'==', email).stream()
                if docs:
                    for doc in docs:
                        userid=doc.id
                picklefilepath= current_path +"/" + userid + ".pkl"
                pickle.dump(footprint, open(picklefilepath, "wb"))
                cloudfilename=userid + ".pkl"
                blob = bucket.blob(cloudfilename)
                blob.upload_from_filename(picklefilepath)
                if blob.public_url and os.path.exists(current_path):
                    shutil.rmtree(current_path, ignore_errors=True) 

            return f"Succesfully created footprint for {email}"         
        else:
            return f"Please upload atleast 3 images"
    except Exception as e:
        return f"An Error Occured: {e}"


@app.route('/fetchuseronimage', methods=['POST'])
@cross_origin()
def fetch_user_onimage():
    try:
        if request.files:
            files = request.files.values()
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['TEMP_FOLDER'], filename))
                    embeddings = create_embeddings(filename,app.config['TEMP_FOLDER'])
            if len(embeddings)>0:
                blobfiles = bucket.list_blobs()
                mindistance = inf
                minuserid = ""
                userfootprints = [file.name for file in blobfiles if '.' in file.name]
                for fp in userfootprints:
                    blob = bucket.blob(fp)
                    blobuserid = blob.name.split('.')[0]
                    blob.download_to_filename(app.config['TEMP_FOLDER'] + blobuserid)
                    cfootprint = pickle.load(open(app.config['TEMP_FOLDER'] + blobuserid,"rb"))

                    #  #Cosine Similarity
                    # s = tf.keras.losses.cosine_similarity(x1,y1)
                    # print("Cosine Similarity:",s)

                    # #Normalized Euclidean Distance
                    # s = tf.norm(tf.nn.l2_normalize(x1, 0)-tf.nn.l2_normalize(y1, 0),ord='euclidean')
                    # print("Normalized Euclidean Distance:",s)

                    #Euclidean Distance
                    s = tf.norm( embeddings-cfootprint, ord='euclidean')
                    print("Euclidean Distance:",s)
                    if s.numpy() < mindistance :
                        mindistance = min (mindistance, s.numpy())
                        minuserid = blobuserid
                doc_ref = users.document(minuserid)
                doc = doc_ref.get()
                if doc.exists:
                    print(f'Document data: {doc.to_dict()}')
                else:
                    print(u'No such document!')
                
            return f"User found for uploaded image {doc.to_dict()}"
        else:
            return f"Please upload atleast 3 images"
    except Exception as e:
        return f"An Error Occured: {e}"




def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_embeddings(image,path):
    try:
        img = Image.open(os.path.join(path, image))
         # Get cropped and prewhitened image tensor
        img_cropped = mtcnn(img)
        # Calculate embedding (unsqueeze to add batch dimension)
        resnet = InceptionResnetV1(pretrained='vggface2').eval()
        img_embedding = resnet(img_cropped.unsqueeze(0))
        # Or, if using for VGGFace2 classification
        resnet.classify = True
        vgg_embeddings = resnet(img_cropped.unsqueeze(0))
        emb = vgg_embeddings 
        emb = emb.clone().detach().requires_grad_(True)
        numpy_emb = emb.detach().numpy()
        print(numpy_emb)
        return numpy_emb

    except Exception as e:
        return f"An Error Occured: {e}"



@app.route("/")
def root():
    # Verify Firebase auth.
    # id_token = request.cookies.get("token")
    # error_message = None
    # claims = None
    # times = None

    # if id_token:
    #     try:
    #         # Verify the token against the Firebase Auth API. This example
    #         # verifies the token on each page load. For improved performance,
    #         # some applications may wish to cache results in an encrypted
    #         # session store (see for instance
    #         # http://flask.pocoo.org/docs/1.0/quickstart/#sessions).
    #         claims = google.oauth2.id_token.verify_firebase_token(
    #             id_token, firebase_request_adapter
    #         )

    #         store_time(claims["email"], datetime.datetime.now())
    #         store_time(datetime.datetime.now())
    #         #times = fetch_times(claims["email"], 10)

    #     except ValueError as exc:
    #         # This will be raised if the token is expired or any other
    #         # verification checks fail.
    #         error_message = str(exc)

    # return render_template(
    #     "index.html", user_data=claims, error_message=error_message, times=times
    # )
    return "base"



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
