from collections import deque
import signal
import subprocess
import time
from typing import Any, Dict
from flask import Flask, render_template, request, jsonify
import threading
import os
import requests
import platform
from werkzeug.serving import run_simple

from Midi.eventLineInterface import EventLineInterface
from Midi.eventLine import EventData, EventLine, EventType
import logging
import globalData

#logging.basicConfig(level=logging.DEBUG)

log_messages = deque(maxlen=20)


class WebServer(EventLineInterface):
    
    def __init__(self, host: str, port: int, folderName: str = 'templates'):
        super().__init__()
        TEMPLATE_FOLDER = WebServer._find_templates_folder(folderName=folderName)
        
        self._app = Flask(__name__, template_folder=TEMPLATE_FOLDER)
        self._app.route('/')(self.index)
        self._app.route('/update', methods=['POST'])(self.update)
        self._app.route('/settings')(self.settings)
        self._app.route('/colors')(self.colors)
        self._app.route('/console')(self.console)
        
        #self._app.add_url_rule('/update', 'update', self.update, methods=['POST'])
        self._app.route('/stop', methods=['GET'])(self.stopServer)
        self._app.route('/logs', methods=['GET'])(self.get_logs)
        self._app.route('/get_settings', methods=['GET'])(self.load_settings)

        self._PID = os.getpid()
        
        print(f"Template folder: {self._app.template_folder}")
        
        self._host: int = host
        self._port: int = port
        
  
    
    @classmethod    
    def _find_templates_folder(self, folderName: str, starting: str = os.getcwd()):
        for dirpath, dirnames, _ in os.walk(starting):
            if folderName in dirnames:
                return os.path.join(dirpath, folderName)
        raise FileNotFoundError(f"Cartella {folderName} non trovata sotto " + starting)
        
    def start(self) -> None:
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()
        
    def stop(self) -> None:
        requests.get(f"http://localhost:{self._port}/stop")
        #self.stopServer()
        
    def get_pid_by_port(self, port):
        
        sytem = platform.system()
        
        if sytem == "Windows":
            result = subprocess.run(f'netstat -ano | findstr :{port}', shell=True, capture_output=True, text=True)
            lines = result.stdout.strip().split("\n")

            if lines:
                parts = lines[0].split()
                pid = parts[-1]  # L'ultimo valore è il PID
                return int(pid)
            return None

        else:
            result = subprocess.run(["lsof", "-i", f":{port}"], capture_output=True, text=True)
            lines = result.stdout.strip().split("\n")
            
            if len(lines) > 1:  # Se trova più di una riga, significa che il server è attivo
                pid = lines[1].split()[1]  # Il PID è la seconda colonna
                return int(pid)
            return None
        
    def stopServer(self):
        # # this mimics a CTRL+C hit by sending SIGINT
        # # it ends the app run, but not the main thread
        # pid = self.get_pid_by_port(self._port)
        # #assert pid == self._PID
        # os.kill(pid, signal.SIGINT)
        # return "OK", 200
        shutdown_func = request.environ.get('werkzeug.server.shutdown')
        if shutdown_func:
            shutdown_func()
        else:
            print("Flask non sta usando Werkzeug! Arresto impossibile.")
            #os.kill(os.getpid(), signal.SIGTERM)  # Kill del processo se necessario
        
        return jsonify(success=True, message="Server Arrestato")
        
    def _run_server(self):
        run_simple(self._host, self._port, self._app, threaded=True)
        #self._app.run(debug=True, use_reloader=False, host=self._host, port=self._port)
        
    def index(self):
        logging.debug("Page requested: 'index.html'")  
        return render_template('index.html', variables=self._variables)
    
    def index(self):
        return render_template('index.html')
    
    def settings(self):
        return render_template('settings.html')#, variables=self._variables)
    
    def colors(self):
        return render_template('colors.html', variables=self._variables)
    
    def console(self):
        return render_template('console.html')
    
    def get_logs(self):
        # Restituisce gli ultimi 100 messaggi
        return jsonify(list(log_messages))

    def load_settings(self):

        data: Dict[str, Dict[str, Any]] = {}

        for i, obj in enumerate(list(globalData.Settings)):
            data[i] = obj.value.jsonData() 


        return jsonify(success=True, variables=data)

    def update(self):
        data = request.get_json(silent=True)
        
        if not(data is None):
            for key, value in data.items():
                if key in self._variables:
                    self._variables[key] = value
            
            logging.info(f"request.get_json: {data}")
            super().notifyEvent(EventData(data, EventType.SETTING_CHANGE)) 
        else:
            logging.debug("request.get_json is None")    
        
        return jsonify(success=True, variables=self._variables)

   










if __name__ == '__main__':
    
    line = EventLine()
    
    print("Starting server...")
    server = WebServer('0.0.0.0', 5001)
    server.OutputLine = line
    server.start()
    print("server started")
    # time.sleep(5)
    # server.stop()
    
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Stopping")


