

from flask import Flask, render_template, request, jsonify
import threading
import os

from Midi.eventLineInterface import EventLineInterface
from Midi.eventLine import EventData, EventLine, EventType
import logging
logging.basicConfig(level=logging.DEBUG)

class WebServer(EventLineInterface):
    
    def __init__(self, host: str, port: int, folderName: str = 'templates'):
        TEMPLATE_FOLDER = WebServer._find_templates_folder(folderName=folderName)
        
        self._app = Flask(__name__, template_folder=TEMPLATE_FOLDER)
        self._app.route('/')(self.index)
        #self._app.route('/update', methods=['POST'])(self.update)
        self._app.add_url_rule('/update', 'update', self.update, methods=['POST'])
        self._app.route('/stop', methods=['GET'])(self.stop)
        
        print(f"Template folder: {self._app.template_folder}")
        
        self._host: int = host
        self._port: int = port
        
        self._variables = {
            "slider1": 50,
            "slider2": 75,
            "button": False
        }
        self.stop_event = threading.Event()
    
    @classmethod    
    def _find_templates_folder(self, folderName: str, starting: str = os.getcwd()):
        for dirpath, dirnames, _ in os.walk(starting):
            if folderName in dirnames:
                return os.path.join(dirpath, folderName)
        raise FileNotFoundError(f"Cartella {folderName} non trovata sotto " + starting)
        
    def start(self) -> None:
        server_thread = threading.Thread(target=self._run_server)
        server_thread.start()
        
    def _run_server(self):
        while not self.stop_event.is_set():
            self._app.run(debug=True, use_reloader=False, host=self._host, port=self._port)
        
    def index(self):
        logging.debug("Page requested: 'index.html'")  
        return render_template('index.html', variables=self._variables)
    
    def update(self):
        data = request.get_json(silent=True)
        
        if not(data is None):
            for key, value in data.items():
                if key in self._variables:
                    self._variables[key] = value
                 
            super().notifyEvent(EventData(data, EventType.SETTING_CHANGE)) 
        else:
            logging.debug("request.get_json is None")    
        
        return jsonify(success=True, variables=self._variables)

    def stop(self):
        self.stop_event.set()
        return jsonify(success=True, message="Server stopping...")

    def run_server(self):
        #while not self.stop_event.is_set():
        self._app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5000)

    def stop_server(self):
        self.stop_event.set()










if __name__ == '__main__':
    
    line = EventLine()
    
    server = WebServer('0.0.0.0', 5000)
    server.OutputLine = line
    server.start()

