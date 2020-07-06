from flask import Flask
from flask import render_template
from flask import request, jsonify, make_response, send_from_directory, redirect

from Cryptodome.Cipher import AES
from Cryptodome import Random
from binascii import b2a_hex, a2b_hex

import os

from moviepy.editor import VideoFileClip


app = Flask(__name__, template_folder='./html')


key = 'fz6mfz6mffffzzzz'.encode('utf-8')
iv = Random.new().read(AES.block_size)


@app.route('/')
def main():
    return render_template('index.html')


@app.route('/uploadfileurl', methods=['POST'])
def upload():
    video = request.files['file']
    if video.content_type != 'video/mp4':
        return 404
    name = video.filename
    video.save('./upload/' + name)
    multiple = request.form.get('multiple')
    videoProcessing(name, float(multiple))
    result = {
        'key': keyEncryption(name),
        'url': '/download/'
    }
    response = make_response(jsonify(result), 200)
    # 设置响应头
    response.headers["Access-Control-Allow-Origin"] = '*'
    return response


def keyEncryption(data):
    global key
    cipher = AES.new(key, AES.MODE_CFB, iv)
    ciphertext = iv + cipher.encrypt(data.encode('utf-8'))
    return b2a_hex(ciphertext).decode('utf-8')


def keyDecrypt(ciphertext):
    ciphertext = a2b_hex(ciphertext.encode('utf-8'))
    decrypt = AES.new(key, AES.MODE_CFB, ciphertext[:16])
    decrypttext = decrypt.decrypt(ciphertext[16:])
    return decrypttext.decode('utf-8')


@app.route('/download/<secret>')
def downloadFile(secret, methods=['GET']):
    try:
        name = keyDecrypt(secret)
        if os.path.exists('./out/' + name):
            return send_from_directory("./out/", filename=name, as_attachment=True)
    except:
        pass
    return 403


def videoProcessing(name, multiple):
    cleanDirectory('out')
    cleanDirectory('upload', name)
    clip = VideoFileClip('./upload/' + name)
    newclip = clip.volumex(multiple)
    newclip.write_videofile('./out/' + name)
    return None


def cleanDirectory(dir, exclude=''):
    fileList = os.listdir('./' + dir)
    try:
        fileList.remove(exclude)
    except:
        pass
    for file in fileList:
        os.remove('./' + dir + '/' + file)


if __name__ == "__main__":
    app.run(port=5555)
