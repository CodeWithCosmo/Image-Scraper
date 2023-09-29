import os
import sys
import base64
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request
from src.exception import CustomException
from src.logger import logging as lg

app = Flask(__name__)
def b64encode_filter(data):
    if isinstance(data, str):
        data = data.encode('utf-8')
    encoded_data = base64.b64encode(data).decode('utf-8')
    return encoded_data

app.jinja_env.filters['b64encode'] = b64encode_filter

@app.route("/", methods = ['GET'])
def homepage():
    return render_template("index.html")

@app.route("/search" , methods = ['POST'])
def index():
        try:
            lg.info('Searching for images')
            # query to search for images
            query = request.form['content'].replace(" ","")

            # directory to store downloaded images
            save_directory = "images/"

            # create the directory if it doesn't exist
            if not os.path.exists(save_directory):
                os.makedirs(save_directory)



            # fake user agent to avoid getting blocked by Google
            header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}

            # fetch the search results page
            response = requests.get(f"https://www.google.com/search?q={query}&sxsrf=AJOqlzUuff1RXi2mm8I_OqOwT9VjfIDL7w:1676996143273&source=lnms&tbm=isch&sa=X&ved=2ahUKEwiq-qK7gaf9AhXUgVYBHYReAfYQ_AUoA3oECAEQBQ&biw=1920&bih=937&dpr=1#imgrc=1th7VhSesfMJ4M")


            # parse the HTML using BeautifulSoup
            soup = BeautifulSoup(response.content, "html.parser")

                # find all img tags
            image_tags = soup.find_all("img")

            # download each image and save it to the specified directory
            del image_tags[0]
            img_data=[]
            for index,image_tag in enumerate(image_tags):
                        # get the image source URL
                        image_url = image_tag['src']
                        #print(image_url)
                        
                        # send a request to the image URL and save the image
                        image_data = requests.get(image_url).content
                        mydict={"Index":index,"Image":image_data}
                        img_data.append(mydict)
                        with open(os.path.join(save_directory, f"{query}_{image_tags.index(image_tag)+1}.jpg"), "wb") as f:
                            f.write(image_data)
            lg.info('Search successful')
            return render_template('index.html',context='Search completed')

        except Exception as e:
            raise CustomException(e,sys)