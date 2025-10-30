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
        self._app.route('/api/settings', methods=['GET', 'POST'])(self.__updateGetSettings)
        self._app.route('/api/piano_settings', methods=['POST'])(self.__updatePianoSettings)
        self._app.route('/api/pedal_settings', methods=['POST'])(self.__updatePedalSettings)
        
    
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
                    PianoLED.ANIMATION_PARAMETRE_NAME : PianoLED.Animation.SOLID_COLOR,
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
                
            elif modalita == 'schema_cromatico':
                msg = EventData({
                    PianoLED.ANIMATION_PARAMETRE_NAME: PianoLED.Animation.CROMATIC,
                    PianoLED.AnimationParametre.BRIGHTNESS: data.get('luminosita'), 
                    PianoLED.AnimationParametre.DELAY: data.get('durata'), 
                    PianoLED.AnimationParametre.MODALITY: data.get('sotto_modalita'), 
                    PianoLED.AnimationParametre.SCHEME: data.get('schema'),
                    PianoLED.AnimationParametre.ANIMATED: data.get('animato', True),
                    PianoLED.AnimationParametre.OFFSET: data.get('offset', 0)
                }, self.__ControlsEvent)
                
            elif modalita == 'schema_cromatico_fade':
                msg = EventData({
                    PianoLED.ANIMATION_PARAMETRE_NAME: PianoLED.Animation.CROMATIC_FADE,
                    PianoLED.AnimationParametre.BRIGHTNESS: data.get('max_luminosita'), 
                    PianoLED.AnimationParametre.FADE_DURATION: data.get('durata_fade'),
                    PianoLED.AnimationParametre.DELAY: data.get('durata_ciclo'), 
                    PianoLED.AnimationParametre.MODALITY: data.get('sotto_modalita'), 
                    PianoLED.AnimationParametre.SCHEME: data.get('schema'),
                    PianoLED.AnimationParametre.ANIMATED: data.get('animato', True),
                    PianoLED.AnimationParametre.OFFSET: data.get('offset', 0)
                }, self.__ControlsEvent)
                
            elif modalita == 'aleatorio_singolo_fade':
                msg = EventData({
                    PianoLED.ANIMATION_PARAMETRE_NAME: PianoLED.Animation.ON_PRESS_FADE,
                    PianoLED.AnimationParametre.COLOR: data.get('colore'), 
                    PianoLED.AnimationParametre.BRIGHTNESS: data.get('max_luminosita'), 
                    PianoLED.AnimationParametre.FADE_DURATION: data.get('durata_fade'),
                }, self.__ControlsEvent)
            
            else:
                return jsonify({"status": "error", "message": f"Modalità '{modalita}' non riconosciuta"}), 400

            print(msg)
            self.notifyEvent(msg, as_thread=True)
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

    def __updatePianoSettings(self) -> Response:
        """Endpoint per aggiornare le impostazioni del piano."""
        new_settings = request.get_json()
        if not new_settings or 'piano' not in new_settings:
            return jsonify({"status": "error", "message": "Nessun dato ricevuto o formato non valido"}), 400
        
        try:
            # Aggiorna la configurazione del piano in memoria
            if 'piano' not in self._config:
                self._config['piano'] = {}
            
            self._config['piano'].update(new_settings['piano'])
            
            # Salva la configurazione su file
            self.__save_config(self._config)
            
            # Invia un evento per notificare il cambiamento delle impostazioni del piano
            if self.__SettingEvent:
                msg = EventData({
                    'type': 'piano_settings',
                    'settings': self._config['piano']
                }, self.__SettingEvent)
                self.notifyEvent(msg, as_thread=True)
            
            return jsonify({
                "status": "success", 
                "message": "Impostazioni del piano salvate con successo."
            })
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    def __updatePedalSettings(self) -> Response:
        """Endpoint per aggiornare le impostazioni dei pedali."""
        new_settings = request.get_json()
        if not new_settings or 'pedals' not in new_settings:
            return jsonify({"status": "error", "message": "Nessun dato ricevuto o formato non valido"}), 400
        
        try:
            # Aggiorna la configurazione dei pedali in memoria
            if 'pedals' not in self._config:
                self._config['pedals'] = {}
            
            self._config['pedals'].update(new_settings['pedals'])
            
            # Salva la configurazione su file
            self.__save_config(self._config)
            
            # Invia un evento per notificare il cambiamento delle impostazioni dei pedali
            if self.__SettingEvent:
                msg = EventData({
                    'type': 'pedal_settings',
                    'settings': self._config['pedals']
                }, self.__SettingEvent)
                self.notifyEvent(msg, as_thread=True)
            
            return jsonify({
                "status": "success", 
                "message": "Impostazioni dei pedali salvate con successo."
            })
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    def __load_config(self) -> Dict[str, Any]:
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Se il file non esiste, ne crea uno con i valori di default
            default_config = {
                "piano": {
                    "transpose": 0,
                    "noteoffset": 21,
                    "piano_white_note_size": 2.4,
                    "piano_black_note_size": 1.0,
                    "led_size": 1.2,
                    "led_number": 78,
                    "max_brightness": 100,
                    "led_pin": 18
                },
                "pedals": {
                    "mode": "animazioni_colori",
                    "animation_gpio": None,
                    "color_gpio": None
                },
                "frontend": {
                    "default_theme": "dark", 
                    "default_color": "#00aaff"
                }
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