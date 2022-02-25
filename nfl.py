from flask import Flask
import subprocess
import os 

dir_path = os.path.dirname(os.path.realpath(__file__))

app = Flask(__name__)

@app.route("/")
def root():
	proc = subprocess.Popen(["python3", dir_path + "/predict.py"], stdout=subprocess.PIPE)
	(out, err) = proc.communicate()
	for i in range(7):
		out = out.replace(i,"<font color='black'>")
	return out, 200

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=5001)

