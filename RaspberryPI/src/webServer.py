from collections import deque
import signal
import subprocess
import time
from typing import Any, Dict, Optional
from flask import Flask, Response, render_template, request, jsonify
import threading
import os
import json
import requests
import platform
from werkzeug.serving import run_simple

from EventLine.eventLineInterface import EventLineInterface
from EventLine.eventLine import EventData, EventLine, Event
from PianoElements.piano import PianoLED
import logging
import globalData

#logging.basicConfig(level=logging.DEBUG)

log_messages = deque(maxlen=20)


class WebServer(EventLineInterface):
    
    def __init__(self, host: str, port: int, folderName: str = 'templates'):
        super().__init__()
        
        self._config = self.__load_config()
        self._PID = os.getpid()
        self._host: int = host
        self._port: int = port
        self.__SettingEvent: Optional[Event] = None
        self.__ControlsEvent: Optional[Event] = None
     
        # TEMPLATE_FOLDER = WebServer._find_templates_folder(folderName=folderName)
        # self._app = Flask(__name__, template_folder=TEMPLATE_FOLDER)
     
        self._app = Flask(__name__)
        self._app.route('/')(self.index)
        self._app.route('/api/control', methods=['POST'])(self.__updateControls)
        self._app.route('/api/settings', methods=['POST'])(self.__updateGetSettings)
        
    
    def setSettingChangeEventType(self, event: Optional[Event]) -> None:
        self.__SettingEvent = event
        
    def setControlsChangeEventType(self, event: Optional[Event]) -> None:
        self.__ControlsEvent = event   
        
    
    @classmethod    
    def _find_templates_folder(self, folderName: str, starting: str = os.getcwd()):
        for dirpath, dirnames, _ in os.walk(starting):
            if folderName in dirnames:
                return os.path.join(dirpath, folderName)
        raise FileNotFoundError(f"Cartella {folderName} non trovata sotto " + starting)


    def index(self):
        return render_template('index.html')


    def __updateControls(self) -> Response:
        """Endpoint API per ricevere comandi di controllo."""
        data = request.get_json()
        
        if not data:
            return jsonify({"status": "error", "message": "Nessun dato ricevuto"}), 400
        
        if self.__ControlsEvent is None:
            logging.warning("evento non impostato")
            return jsonify({"status": "error", "message": "evento non impostato"}), 500
            
        modalita = data.get('modalita')
        
        try:
            if modalita == 'spegni':
                msg = EventData({
                    PianoLED.ANIMATION_PARAMETRE_NAME : PianoLED.Animation.OFF
                }, self.__ControlsEvent)
                
            elif modalita == 'tutti_fissi':
                msg = EventData({
                    PianoLED.ANIMATION_PARAMETRE_NAME : PianoLED.Animation.OFF,
                    PianoLED.AnimationParametre.COLOR: data.get('colore'), 
                    PianoLED.AnimationParametre.BRIGHTNESS: data.get('luminosita'), 
                }, self.__ControlsEvent)
                
            elif modalita == 'aleatorio_singolo':
                msg = EventData({
                    PianoLED.ANIMATION_PARAMETRE_NAME: PianoLED.Animation.ON_PRESS,
                    PianoLED.AnimationParametre.COLOR: data.get('colore'), 
                    PianoLED.AnimationParametre.BRIGHTNESS: data.get('luminosita'), 
                    PianoLED.AnimationParametre.DELAY: data.get('durata'),
                }, self.__ControlsEvent)
                
            elif modalita == 'aleatorio_singolo':
                msg = EventData({
                    PianoLED.ANIMATION_PARAMETRE_NAME: PianoLED.Animation.RANDOM_COLOR,
                    PianoLED.AnimationParametre.COLOR: data.get('colore'), 
                    PianoLED.AnimationParametre.BRIGHTNESS: data.get('luminosita'), 
                    PianoLED.AnimationParametre.DELAY: data.get('durata'), 
                }, self.__ControlsEvent)
                
            elif modalita == 'schema_cromatico':
                msg = EventData({
                    PianoLED.ANIMATION_PARAMETRE_NAME: PianoLED.Animation.CROMATIC,
                    PianoLED.AnimationParametre.BRIGHTNESS: data.get('luminosita'), 
                    PianoLED.AnimationParametre.DELAY: data.get('durata'), 
                    PianoLED.AnimationParametre.MODALITY: data.get('sotto_modalita'), 
                    PianoLED.AnimationParametre.SCHEME: data.get('schema'), 
                }, self.__ControlsEvent)
                
            elif modalita == 'aleatorio_singolo_fade':
                #led_controller.avvia_aleatorio_singolo_fade(data.get('colore'), data.get('max_luminosita'), data.get('durata_fade'))
                logging.warning("aleatorio_singolo_fade non implementato")
            
            else:
                return jsonify({"status": "error", "message": f"Modalità '{modalita}' non riconosciuta"}), 400


            print(msg)
            self.notifyEvent(msg, as_thread = True)
            return jsonify({"status": "success", "message": f"Modalità '{modalita}' applicata con successo."})

        except Exception as e:
            print(e)
            return jsonify({"status": "error", "message": str(e)}), 500
      
        
    def __updateGetSettings(self) -> Response:
        """Endpoint per leggere e scrivere le impostazioni di configurazione."""
        if request.method == 'GET':
            # Restituisce la configurazione attuale
            return jsonify(self._config)
        
        if request.method == 'POST':
            new_settings = request.get_json()
            if not new_settings:
                return jsonify({"status": "error", "message": "Nessun dato ricevuto"}), 400
            
            # Aggiorna la configurazione in memoria
            self._config.update(new_settings)
            
            # Salva la configurazione su file
            self.__save_config(self._config)
            
            # NOTA: Le modifiche hardware richiedono un riavvio del server per essere applicate.
            return jsonify({
                "status": "success", 
                "message": "Impostazioni salvate. Riavvia il server per applicare le modifiche hardware."
            })



    def __load_config(self) -> Dict[str, Any]:
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError or json.JSONDecodeError:
            # Se il file non esiste, ne crea uno con i valori di default
            default_config = {
                "hardware": {"led_count": 74, "led_pin": 18},
                "frontend": {"default_theme": "dark", "default_color": "#00aaff"}
            }
            self.__save_config(default_config)
            return default_config
    

    def __save_config(self, config_data: dict) -> None:
        with open('config.json', 'w') as f:
            json.dump(config_data, f, indent=4)


    def handleEvent(self, event):
        pass

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
    
    def get_logs(self):
        # Restituisce gli ultimi 100 messaggi
        return jsonify(list(log_messages))

    # def load_settings(self):

    #     data: Dict[str, Dict[str, Any]] = {}

    #     for i, obj in enumerate(list(globalData.Settings)):
    #         data[i] = obj.value.jsonData() 


    #     return jsonify(success=True, variables=data)

    # def update(self):
    #     data = request.get_json(silent=True)
        
    #     if not(data is None):
    #         for key, value in data.items():
    #             if key in self._variables:
    #                 self._variables[key] = value
            
    #         logging.info(f"request.get_json: {data}")
    #         super().notifyEvent(EventData(data, Event.SETTING_CHANGE)) 
    #     else:
    #         logging.debug("request.get_json is None")    
        
    #     return jsonify(success=True, variables=self._variables)

   










if __name__ == '__main__':
    
    #line = EventLine()
    
    print("Starting server...")
    server = WebServer('0.0.0.0', 5001)
    #server.OutputLine = line
    server.start()
    print("server started")
    # time.sleep(5)
    # server.stop()
    
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Stopping")


