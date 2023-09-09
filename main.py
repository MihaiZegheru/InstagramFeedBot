import base64
import requests
import json
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 
import textwrap


IMAGE_SIZE = 256
BORDER_SIZE = 10
TEXT_AREA_HIGHT = 70

IMAGES_PATH = "./images/"
user_access_token = ""
ig_user_id = ""
key = ""


def GeneratePrompt():
    response = requests.get('https://funnysentences.com/res/ajax/generator.php')
    return response.content.decode('UTF-8')

def GenerateAIImages(prompt):
    body = {
        "prompt": prompt
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url="https://backend.craiyon.com/generate", json=body, headers=headers)
    return json.loads(response.content.decode('UTF-8'))['images']

def CreatePostImage(base64Images, prompt):
    for i in range(9):
        decoded_data=base64.b64decode((base64Images[i]))
        
        img_file = open(IMAGES_PATH + "image" + str(i) + ".png", 'wb')
        img_file.write(decoded_data)
        img_file.close()

    finalImage = Image.new("RGB", (IMAGE_SIZE * 3 + 40, IMAGE_SIZE * 3 + TEXT_AREA_HIGHT + 40), "black")

    

    for y in range(3):
        for x in range(3):
            currImage = Image.open(IMAGES_PATH + "image" + str(y * 3 + x) + ".png")
            imageY = y * IMAGE_SIZE + y * 10 + 10
            imageX = x * IMAGE_SIZE + x * 10 + 10 + TEXT_AREA_HIGHT

            finalImage.paste(currImage, (imageY, imageX))

    draw = ImageDraw.Draw(finalImage)
    font = ImageFont.truetype("arial.ttf", 22)
    imageWidth, imageHeight = finalImage.size
    

    margin = offset = 5
    for line in textwrap.wrap(prompt, width=55):
        textWidth, textHeight = draw.textsize(line, font=font)
        draw.text(((imageWidth - textWidth) / 2, offset), line, (255,255,255), font=font)
        offset += textHeight + 1

    finalImage.save(IMAGES_PATH + "finalImage.jpg")


def UploadImage():
    data = {
        "key": key
    }
    files={'media': open(IMAGES_PATH + "finalImage.jpg",'rb')}

    response = requests.post(url="https://thumbsnap.com/api/upload", data=data, files=files)
    response = json.loads(response.text)

    return str(response["data"]["media"])

def GenerateCaption(prompt):
    caption = prompt + "\n.\n.\n.\n.\n.\n.\n#viral #dalle #haha #art #memepage #instagram #ai #shitpost #meme #memes #like #like4like #cursedmemes #weirdcore #memesdaily #fun #generated #photo #likeforlike #funnymemes #instadaily #funny #laugh #computer #creepy #lol #dankmeme #l4l #comment #memesdaily"
    return caption

def PostInstagramQuote(imageURLLocation, prompt):
    post_url = 'https://graph.facebook.com/v14.0/{}/media'.format(ig_user_id)
    caption = GenerateCaption(prompt=prompt)
    payload = {
        'image_url': imageURLLocation,
        'caption': caption,
        'access_token': user_access_token
    }
    r = requests.post(post_url, data=payload)
    result = json.loads(r.text)

    if 'id' in result:
        creation_id = result['id']
        second_url = 'https://graph.facebook.com/v10.0/{}/media_publish'.format(ig_user_id)
        second_payload = {
            'creation_id': creation_id,
            'access_token': user_access_token
        }
        r = requests.post(second_url, data=second_payload)
        print('--------Just posted to instagram--------')
        print(r.text)
    else:
        print(r.content)



prompt = GeneratePrompt()
print(prompt)

base64Images = GenerateAIImages(prompt=prompt)
CreatePostImage(base64Images=base64Images, prompt=prompt)

mediaURL = UploadImage()
PostInstagramQuote(imageURLLocation=mediaURL, prompt=prompt)
