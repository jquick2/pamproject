from flask import Flask, render_template, request, jsonify
import re
from PIL import Image
import pytesseract
import base64

app = Flask(__name__)

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/about")
def about():
	return render_template("about.html")

@app.route("/text")
def text():
	return render_template("text.html")

@app.route("/image")
def image():
	return render_template("image.html")

@app.route("/file")
def file():
	return render_template("file.html")

@app.route("/iosappimagepost", methods=["POST"])
def iosimage():
	jsonstuff = request.json
	image64 = jsonstuff["image"]
	imgdata = base64.b64decode(image64)
	
	fh = open('imageToSave.png', 'wb')
	fh.write(imgdata)
	fh.close()
	image = Image.open('imageToSave.png')
	sequence = pytesseract.image_to_string(image, lang="eng")
	print(sequence)
	return jsonify(modSequence=sequence)


@app.route("/results", methods=["POST"])
def results():
	#if not request.form.get("sequence"):
	#	return render_template("error.html")

	if request.form.get("sequence") != None:
		sequence = request.form.get("sequence")

	elif request.form.get("seqimg") != None:
		image = Image.open(request.form.get("seqimg"))
		sequence = pytesseract.image_to_string(image, lang="eng")

	else:
		f = open("samplefasta.txt", "r")
		sequence = f.read().upper()

	selector = int(request.form.get("selector"))

	print(sequence)
	print(selector)

	results = sequence
	nucleases = ""

	if selector == 1 and re.search('[ATCG]GG',results):
	  nucleases += "SpCas9 "
	  results = re.sub(r'([ATCG]GG)',r'[\1]',results)
	  
	if selector == 2 and re.search('[ATCG]G[AG][AG][AGTC]',results):
	  nucleases += "SaCas9 "
	  results = re.sub(r'([ATCG]G[AG][AG][AGTC])',r'[\1]',results)
	  
	if selector == 3 and re.search('[ATCG][ATCG][ATCG][ATCG]GATT',results):
	  nucleases += "NmeCas9 "
	  results = re.sub(r'([ATCG][ATCG][ATCG][ATCG]GATT)',r'[\1]',results)
	  
	if selector == 4 and re.search('[ATCG][ATCG][ATCG][ATCG][AG][CT]AC',results):
	  nucleases += "CjCas9"
	  results = re.sub(r'([ATCG][ATCG][ATCG][ATCG][AG][CT]AC)',r'[\1]',results)
	  
	if selector == 5 and re.search('[ATCG][ATCG]AGAA[AT]',results):
	  nucleases += "StCas6"
	  results = re.sub(r'([ATCG][ATCG]AGAA[AT])',r'[\1]',results)
	  
	if selector == 6 and re.search('TTT[ACG]',results):
	  nucleases += "LbCpf1"
	  results = re.sub(r'(TTT[ACG])',r'[\1]',results)
	  
	if selector == 7 and re.search('TTT[ACG]',results):
	  nucleases += "AsCpf1"
	  results = re.sub(r'(TTT[ACG])',r'[\1]',results)

	results = re.sub("(.{60})", "\\1\n", results, 0, re.DOTALL)

	print(results)

	return render_template("results.html", results=results, nucleases=nucleases)