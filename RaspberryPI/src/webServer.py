

from flask import Flask, render_template, request, jsonify
import threading

app = Flask(__name__)

# Variabili sul server
variables = {
    "slider1": 50,
    "slider2": 75,
    "button": False
}

stop_event = threading.Event()

@app.route('/')
def index():
    return render_template('/home/matty234/Desktop/GIT_HUB/MIDI-PIANO_LED/RaspberryPI/src/index.html', variables=variables)

@app.route('/update', methods=['POST'])
def update():
    data = request.json
    for key, value in data.items():
        if key in variables:
            variables[key] = value
    return jsonify(success=True, variables=variables)

@app.route('/stop', methods=['POST'])
def stop():
    stop_event.set()
    return jsonify(success=True, message="Server stopping...")

def run_server():
    while not stop_event.is_set():
        app.run(debug=True, use_reloader=False)

if __name__ == '__main__':
    server_thread = threading.Thread(target=run_server)
    server_thread.start()
    
    try:
        while not stop_event.is_set():
            pass
    except KeyboardInterrupt:
        stop_event.set()
        server_thread.join()
