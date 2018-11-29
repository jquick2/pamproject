from flask import Flask, render_template, request, jsonify
import re
from PIL import Image
import pytesseract
import base64
import cv2
from werkzeug import secure_filename


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
	selector = 1
	cut = (1,3)

	results, nucleases = get_info(sequence, selector, cut, "", "")
	print('here')
	return render_template("results.html", results=results, nucleases="SpCas9")


@app.route("/results", methods=["POST"])
def results():
	#if not request.form.get("sequence"):
	#	return render_template("error.html")

	cut_start = int(request.form.get("cut_start"))
	cut_end = int(request.form.get("cut_end"))

	if request.form.get("sequence") != None:
		sequence = request.form.get("sequence")

	elif 'seqimg' in request.files:
		print ("in here")
		newImage = Image.open(request.files['seqimg'])
		sequence = pytesseract.image_to_string(newImage, lang="eng", config='--psm 6 --oem 3 -c tessedit_char_whitelist=acgtACGT')
		print(sequence)

	elif 'fileseq' in request.files:
		file = open("samplefasta.txt", "r")
		sequencealllines = file.read().upper()
		sequence = '\n'.join(sequencealllines.split('\n')[1:])

	selector = int(request.form.get("selector"))

	cut = (cut_start-1,cut_end)


	Engineered_Nuclease_PAM = request.form.get('Engineered_Nuclease_PAM')
	EngineeredNuclease = request.form.get('prime')
	print(EngineeredNuclease)
	print(Engineered_Nuclease_PAM)
	results, nucleases = get_info(sequence, selector, cut, Engineered_Nuclease_PAM, EngineeredNuclease)

	return render_template("results.html", results=results, nucleases=nucleases)



# Allows user to put the <> around a nucleotide without messing up search.
def fix_s(ori,sub):
	ori_chk = [a.isalpha() for a in list(ori)]
	sub_chk = [a.isalpha() for a in list(sub)]

	N = 0
	for i in ori_chk:
		if i: N += 1
	
	n = 0
	i = 0
	j = 0
	new_sub_str = ""
	while(n < N):
	#print(n,i,j,new_sub_str)
		if ori_chk[i] and sub_chk[j]:
			new_sub_str += sub[j]
			n += 1
			i += 1
			j += 1
		if i < len(ori_chk) and ori_chk[i] == False and (j == len(sub_chk) or sub_chk[j]):
			new_sub_str += ori[i]
			i += 1
		if j < len(sub_chk) and sub_chk[j] == False and (i == len(ori_chk) or ori_chk[i]):
			new_sub_str += sub[j]
			j += 1
	
		if i < len(ori_chk) and ori_chk[i] == False and j < len(sub_chk) and sub_chk[j] == False:
			new_sub_str += ori[i] + sub[j]
			i += 1
			j += 1
	
	return new_sub_str


# reverse complement of the various nucleotides
def reverse_complement(dna):
	complement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A', 'R': 'Y', 'Y': 'R', 'V': 'B', 'B': 'V', 'H': 'D', 'D': 'H', 'M': 'K', 'K': 'M'}
	return ''.join([complement[base] for base in dna[::-1]])


def get_info(sequence, selector, cut, Engineered_Nuclease_PAM, EngineeredNuclease):
	results = []
	nucleases = ""


	seq = sequence.replace("<","").replace(">","")

	if selector == 1 and re.search('[ATCG]GG|CC[ATCG]',seq):
		nucleases += "SpCas9"
		for m in re.finditer(r'([ATCG]GG)',seq): #for finding the template
			s = m.start()
			e = m.end()
			g = m.group()
		
			s0 = max(0,s-cut[0])
			s1 = max(0,s-cut[1])

		
			results.append(fix_s(sequence, seq[:s1]+"{"+seq[s1:s0]+"}"+seq[s0:s]+"["+g+"]"+seq[e:]))
		
		for m in re.finditer(r'(CC[ATCG])',seq):
			s = m.start()
			e = m.end()
			g = m.group()
		
			s0 = max(-1, e+cut[0])
			s1 = max(-1, e+cut[1])
		
			results.append(fix_s(sequence, seq[:s]+"["+g+"]"+seq[e:s0]+"{"+seq[s0:s1]+"}"+seq[s1:]))
	
	if selector == 2 and re.search('[ATCG]G[AG][AG][AGTC]|[AGTC][TC][TC]C[ATCG]',seq):
		nucleases += "SaCas9"
		
		for m in re.finditer(r'([ATCG]G[AG][AG][AGTC])',seq): #for finding the template
			s = m.start()
			e = m.end()
			g = m.group()
		
			s0 = max(0,s-cut[0])
			s1 = max(0,s-cut[1])
		
			results.append(fix_s(sequence, seq[:s1]+"{"+seq[s1:s0]+"}"+seq[s0:s]+"["+g+"]"+seq[e:]))
		
		for m in re.finditer(r'([AGTC][TC][TC]C[ATCG])',seq):
			s = m.start()
			e = m.end()
			g = m.group()
		
			s0 = max(-1, e+cut[0])
			s1 = max(-1, e+cut[1])
		
			results.append(fix_s(sequence, seq[:s]+"["+g+"]"+seq[e:s0]+"{"+seq[s0:s1]+"}"+seq[s1:]))
	
	
	if selector == 3 and re.search('[ATCG][ATCG][ATCG][ATCG]GATT|AATC[ATCG][ATCG][ATCG][ATCG]',seq):
		nucleases += "NmeCas9"
		
		for m in re.finditer(r'([ATCG][ATCG][ATCG][ATCG]GATT)',seq): #for finding the template
			s = m.start()
			e = m.end()
			g = m.group()
		
			s0 = max(0,s-cut[0])
			s1 = max(0,s-cut[1])
			
			results.append(fix_s(sequence, seq[:s1]+"{"+seq[s1:s0]+"}"+seq[s0:s]+"["+g+"]"+seq[e:])) 
			
		for m in re.finditer(r'(AATC[ATCG][ATCG][ATCG][ATCG])',seq):
			s = m.start()
			e = m.end()
			g = m.group()
		
			s0 = max(-1, e+cut[0])
			s1 = max(-1, e+cut[1])
		
			results.append(fix_s(sequence, seq[:s]+"["+g+"]"+seq[e:s0]+"{"+seq[s0:s1]+"}"+seq[s1:]))
		
	
	if selector == 4 and re.search('[ATCG][ATCG][ATCG][ATCG][AG][CT]AC|GT[GA][TC][ATCG][ATCG][ATCG][ATCG]',seq):
		nucleases += "CjCas9"
		 
		for m in re.finditer(r'([ATCG][ATCG][ATCG][ATCG][AG][CT]AC)',seq): #for finding the template
			s = m.start()
			e = m.end()
			g = m.group()
		
			s0 = max(0,s-cut[0])
			s1 = max(0,s-cut[1])
			results.append(fix_s(sequence, seq[:s1]+"{"+seq[s1:s0]+"}"+seq[s0:s]+"["+g+"]"+seq[e:])) 
			
		for m in re.finditer(r'(GT[GA][TC][ATCG][ATCG][ATCG][ATCG])',seq):
			s = m.start()
			e = m.end()
			g = m.group()
		
			s0 = max(-1, e+cut[0])
			s1 = max(-1, e+cut[1])
		
			results.append(fix_s(sequence, seq[:s]+"["+g+"]"+seq[e:s0]+"{"+seq[s0:s1]+"}"+seq[s1:]))
		
	
	if selector == 5 and re.search('[ATCG][ATCG]AGAA[AT]|[TA]TTCT[ATCG][ATCG]',seq):
		nucleases += "StCas6"
		
		for m in re.finditer(r'([ATCG][ATCG]AGAA[AT])',seq): #for finding the template
			s = m.start()
			e = m.end()
			g = m.group()
		
			s0 = max(0,s-cut[0])
			s1 = max(0,s-cut[1])
			results.append(fix_s(sequence, seq[:s1]+"{"+seq[s1:s0]+"}"+seq[s0:s]+"["+g+"]"+seq[e:])) 
			
		for m in re.finditer(r'([TA]TTCT[ATCG][ATCG])',seq):
			s = m.start()
			e = m.end()
			g = m.group()
		
			s0 = max(-1, e+cut[0])
			s1 = max(-1, e+cut[1])
		
			results.append(fix_s(sequence, seq[:s]+"["+g+"]"+seq[e:s0]+"{"+seq[s0:s1]+"}"+seq[s1:]))
		
		
	if selector == 6 and re.search('TTT[ACG]|[TGC]AAA',seq):
		nucleases += "LbCpf1"
		
		for m in re.finditer(r'([TGC]AAA)',seq): #for finding the template
			s = m.start()
			e = m.end()
			g = m.group()
		
			s0 = max(0,s-cut[0])
			s1 = max(0,s-cut[1])
			results.append(fix_s(sequence, seq[:s1]+"{"+seq[s1:s0]+"}"+seq[s0:s]+"["+g+"]"+seq[e:])) 
			
		for m in re.finditer(r'(TTT[ACG])',seq):
			s = m.start()
			e = m.end()
			g = m.group()
		
			s0 = max(-1, e+cut[0])
			s1 = max(-1, e+cut[1])
		
			results.append(fix_s(sequence, seq[:s]+"["+g+"]"+seq[e:s0]+"{"+seq[s0:s1]+"}"+seq[s1:]))
	
	
	if selector == 7 and re.search('TTT[ACG]|[TGC]AAA',seq):
		nucleases += "AsCpf1"
		for m in re.finditer(r'([TGC]AAA)',seq): #for finding the template
			s = m.start()
			e = m.end()
			g = m.group()
		
			s0 = max(0,s-cut[0])
			s1 = max(0,s-cut[1])
			results.append(fix_s(sequence, seq[:s1]+"{"+seq[s1:s0]+"}"+seq[s0:s]+"["+g+"]"+seq[e:])) 
			
		for m in re.finditer(r'(TTT[ACG])',seq):
			s = m.start()
			e = m.end()
			g = m.group()
		
			s0 = max(-1, e+cut[0])
			s1 = max(-1, e+cut[1])
		
			results.append(fix_s(sequence, seq[:s]+"["+g+"]"+seq[e:s0]+"{"+seq[s0:s1]+"}"+seq[s1:]))

	if selector == 8:
		PAM = Engineered_Nuclease_PAM
		ReversePAM = (reverse_complement(PAM))
		for r in (("R", "[AG]"), ("Y", "[CT]"), ("S", "[GC]"), ("W", "[AT]"), ("K", "[GT]"), ("M", "[AC]"), ("B", "[CGT]"), ("D", "[AGT]"), ("H", "[ACT]"), ("V", "[ACG]")):
			PAM = PAM.replace(*r)
			ReversePAM = ReversePAM.replace(*r)
			
		if EngineeredNuclease != "" and re.search("""%s""" % (PAM + "|" + ReversePAM), seq):
			nucleases = "EngineeredNuclease"
			if EngineeredNuclease == "Five_Three": 
				for m in re.finditer(r'%s' %("(" + PAM + ")"),seq): #for finding the template
					s = m.start()
					e = m.end()
					g = m.group()
			
					s0 = max(0,s-cut[0])
					s1 = max(0,s-cut[1])
					results.append(fix_s(sequence, seq[:s1]+"{"+seq[s1:s0]+"}"+seq[s0:s]+"["+g+"]"+seq[e:]))
				
				for m in re.finditer(r'%s' %("(" + ReversePAM + ")"),seq):
					s = m.start()
					e = m.end()
					g = m.group()
				
					s0 = max(-1, e+cut[0])
					s1 = max(-1, e+cut[1])
				
					results.append(fix_s(sequence, seq[:s]+"["+g+"]"+seq[e:s0]+"{"+seq[s0:s1]+"}"+seq[s1:]))
				
			if EngineeredNuclease == "Three_Five": 
				for m in re.finditer(r'%s' %("(" + ReversePAM + ")"),seq): #for finding the template
					s = m.start()
					e = m.end()
					g = m.group()
				
					s0 = max(0,s-cut[0])
					s1 = max(0,s-cut[1])
					results.append(fix_s(sequence, seq[:s1]+"{"+seq[s1:s0]+"}"+seq[s0:s]+"["+g+"]"+seq[e:]))
				
				for m in re.finditer(r'%s' %("(" + PAM + ")"),seq):
					s = m.start()
					e = m.end()
					g = m.group()
				
					s0 = max(-1, e+cut[0])
					s1 = max(-1, e+cut[1])
			
					results.append(fix_s(sequence, seq[:s]+"["+g+"]"+seq[e:s0]+"{"+seq[s0:s1]+"}"+seq[s1:]))
				 



	for result in results:
		result = re.sub("(.{40})", "\\1\n", result, 0, re.DOTALL)



	print(results)

	return results, nucleases



