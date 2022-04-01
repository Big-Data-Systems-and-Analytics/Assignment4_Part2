import io
from multiprocessing.spawn import import_main_path
import os
import uvicorn
from fastapi import FastAPI, Body, Depends
from fastapi.responses import FileResponse
from fastapi.responses import Response
from requestmodel import Request
from starlette.responses import StreamingResponse
import sys
import visualize
import gcsfs
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))
from dataprocessing.query_filename import query_filename
from dataprocessing.make_nowcast_dataset import make_nowcast_dataset
from app.api_model import PostSchema, UserSchema, UserLoginSchema
from app.auth.auth_bearer import JWTBearer
from app.auth.auth_handler import signJWT



users = []

app = FastAPI()

#Index route
@app.get('/')
def index():
    return {'message':'Welcome to Nowcasting API'}

@app.post('/predict')
def predict(data:Request): 

    data = data.dict()
    location = data['location']
    begintime = data['begintime']
    endtime = data['endtime']
    if(len(location) == 0 or len(begintime) == 0 or len(endtime) == 0 ):
        return "Enter all the fields"

    filename,fileindex = query_filename(location,begintime,endtime)

    if(filename != 'nofile'):
        input = make_nowcast_dataset(filename,fileindex)
        buf = visualize.predict_data(input,fileindex)
        print(buf)
        #with gcs.open(gcs_file_path) as f:
         #   img = f.imread('g4g.png')
            
        #return FileResponse(buf.read(),media_type="image/png")
        return StreamingResponse(buf,media_type="image/png")
    else:
        return "Location not found. Please try different location"


def check_user(data:UserLoginSchema):
    for user in users:
        print(users)
        if user.email == data.email and user.password == data.password:
         return True      
        return False
    

@app.post("/user/signup", tags=["user"])
def user_signup(user : UserSchema = Body(default=None)):
    users.append(user)
    return signJWT(user.email)


@app.post("/user/login", tags=["user"])
def user_login(user : UserLoginSchema = Body(default = None)):
    if check_user(user):
        return signJWT(user.email)
    else:
        return {

            "error" : "Invalid login details!"
        }

    
if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)

