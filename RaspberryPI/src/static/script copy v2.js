document.addEventListener('DOMContentLoaded', () => {
    const navButtons = document.querySelectorAll('.nav-button');
    const panels = document.querySelectorAll('.control-panel');
    const activateButtons = document.querySelectorAll('.btn-activate');
    const btnSpegni = document.getElementById('btn-spegni-tutto');

    // --- Elementi delle impostazioni ---
    const themeToggle = document.getElementById('theme-toggle');
    const themeText = document.querySelector('.toggle-text');
    const colorSwatches = document.querySelectorAll('.color-swatch');
    const btnSaveHw = document.getElementById('btn-save-hw-settings');
    const btnSavePiano = document.getElementById('btn-save-piano-settings');
    const btnSavePedal = document.getElementById('btn-save-pedal-settings');
    const inputLedCount = document.getElementById('setting-led-count');
    const inputLedPin = document.getElementById('setting-led-pin');
    
    // Elementi per le impostazioni del piano
    const inputTranspose = document.getElementById('setting-transpose');
    const inputNoteOffset = document.getElementById('setting-noteoffset');
    const inputPianoWhiteNoteSize = document.getElementById('setting-piano-white-note-size');
    const inputPianoBlackNoteSize = document.getElementById('setting-piano-black-note-size');
    const inputLedSize = document.getElementById('setting-led-size');
    const inputLedNumber = document.getElementById('setting-led-number');
    const inputMaxBrightness = document.getElementById('setting-max-brightness');
    
    // Elementi per le impostazioni dei pedali
    const inputPedalMode = document.getElementById('setting-pedal-mode');
    const inputPedalAnimation = document.getElementById('setting-pedal-animation');
    const inputPedalColor = document.getElementById('setting-pedal-color');

    // --- Funzione per inviare comandi al backend ---
    async function sendCommand(payload) {
        try {
            const response = await fetch('/api/control', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            const result = await response.json();
            if (!response.ok) throw new Error(result.message || 'Errore nel comando');
            console.log('Successo:', result.message);
        } catch (error) {
            console.error('Errore:', error);
            alert('Impossibile inviare il comando: ' + error.message);
        }
    }

    // --- Logica per il cambio di pannello (Tab) ---
    function switchPanel(targetId) {
        navButtons.forEach(btn => btn.classList.remove('active'));
        panels.forEach(panel => panel.classList.remove('active'));
        const activeButton = document.querySelector(`.nav-button[data-target="${targetId}"]`);
        const activePanel = document.getElementById(targetId);
        if (activeButton && activePanel) {
            activeButton.classList.add('active');
            activePanel.classList.add('active');
        }
    }

    navButtons.forEach(button => {
        button.addEventListener('click', () => switchPanel(button.dataset.target));
    });

    btnSpegni.addEventListener('click', () => sendCommand({ modalita: 'spegni' }));

    activateButtons.forEach(button => {
        if (button.id === 'btn-save-hw-settings' || 
            button.id === 'btn-save-piano-settings' || 
            button.id === 'btn-save-pedal-settings') return; // Esclude i bottoni di salvataggio
        
        button.addEventListener('click', (e) => {
            const panel = e.target.closest('.control-panel');
            const mode = panel.id;
            let payload = { modalita: mode };
            
            if (mode === 'tutti_fissi') {
                payload.colore = panel.querySelector('#colore-tutti').value;
                payload.luminosita = parseInt(panel.querySelector('#luminosita-tutti').value);
            } else if (mode === 'aleatorio_singolo') {
                payload.colore = panel.querySelector('#colore-aleatorio').value;
                payload.luminosita = parseInt(panel.querySelector('#luminosita-aleatorio').value);
                payload.durata = parseInt(panel.querySelector('#durata-aleatorio').value);
            } else if (mode === 'schema_cromatico') {
                payload.sotto_modalita = panel.querySelector('#sotto-modalita-schema').value;
                payload.schema = panel.querySelector('#schema-colore').value;
                payload.animato = panel.querySelector('#animazione-schema').checked;
                payload.offset = parseInt(panel.querySelector('#offset-schema').value);
                payload.luminosita = parseInt(panel.querySelector('#luminosita-schema').value);
                payload.durata = parseInt(panel.querySelector('#durata-schema').value);
            } else if (mode === 'schema_cromatico_fade') {
                payload.sotto_modalita = panel.querySelector('#sotto-modalita-schema-fade').value;
                payload.schema = panel.querySelector('#schema-colore-fade').value;
                payload.animato = panel.querySelector('#animazione-schema-fade').checked;
                payload.offset = parseInt(panel.querySelector('#offset-schema-fade').value);
                payload.max_luminosita = parseInt(panel.querySelector('#max-luminosita-schema-fade').value);
                payload.durata_fade = parseInt(panel.querySelector('#durata-fade-schema').value);
                payload.durata_ciclo = parseInt(panel.querySelector('#durata-ciclo-schema-fade').value);
            } else if (mode === 'aleatorio_singolo_fade') {
                payload.colore = panel.querySelector('#colore-fade').value;
                payload.max_luminosita = parseInt(panel.querySelector('#max-luminosita-fade').value);
                payload.durata_fade = parseInt(panel.querySelector('#durata-fade').value);
            }
            sendCommand(payload);
        });
    });

    // --- Logica per le Impostazioni ---

    // Carica le impostazioni dal backend e dal localStorage
    async function loadAllSettings() {
        try {
            const response = await fetch('/api/settings');
            const serverSettings = await response.json();

            // Popola i campi hardware
            inputLedCount.value = serverSettings.hardware.led_count;
            inputLedPin.value = serverSettings.hardware.led_pin;
            
            // Popola i campi del piano
            inputTranspose.value = serverSettings.piano.transpose || 0;
            inputNoteOffset.value = serverSettings.piano.noteoffset || 21;
            inputPianoWhiteNoteSize.value = serverSettings.piano.piano_white_note_size || 2.4;
            inputPianoBlackNoteSize.value = serverSettings.piano.piano_black_note_size || 1.0;
            inputLedSize.value = serverSettings.piano.led_size || 1.2;
            inputLedNumber.value = serverSettings.piano.led_number || 78;
            inputMaxBrightness.value = serverSettings.piano.max_brightness || 100;
            
            // Popola i campi dei pedali
            inputPedalMode.value = serverSettings.pedals.mode || 'animazioni_colori';
            inputPedalAnimation.value = serverSettings.pedals.animation_gpio || '';
            inputPedalColor.value = serverSettings.pedals.color_gpio || '';

            // Applica le impostazioni frontend di default dal server
            applyTheme(serverSettings.frontend.default_theme);
            applyAccentColor(serverSettings.frontend.default_color);

        } catch (error) {
            console.error("Impossibile caricare le impostazioni dal server:", error);
        }

        // Sovrascrivi con le preferenze salvate nel browser
        const savedTheme = localStorage.getItem('theme') || 'dark';
        const savedColor = localStorage.getItem('accentColor');
        applyTheme(savedTheme);
        if (savedColor) applyAccentColor(savedColor);
    }

    // Applica il tema
    function applyTheme(theme) {
        if (theme === 'light') {
            document.body.classList.add('light-theme');
            themeToggle.checked = true;
            themeText.textContent = 'Chiaro';
        } else {
            document.body.classList.remove('light-theme');
            themeToggle.checked = false;
            themeText.textContent = 'Scuro';
        }
    }

    // Applica il colore primario
    function applyAccentColor(color) {
        document.documentElement.style.setProperty('--accent-color', color);
        colorSwatches.forEach(swatch => {
            swatch.classList.toggle('active', swatch.dataset.color === color);
        });
    }

    // Salva le impostazioni hardware
    async function saveHardwareSettings() {
        const newHwSettings = {
            hardware: {
                led_count: parseInt(inputLedCount.value),
                led_pin: parseInt(inputLedPin.value)
            }
        };
        try {
            const response = await fetch('/api/settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(newHwSettings),
            });
            const result = await response.json();
            if (!response.ok) throw new Error(result.message);
            alert(result.message);
        } catch (error) {
            console.error('Errore:', error);
            alert('Impossibile salvare le impostazioni hardware: ' + error.message);
        }
    }
    
    // Salva le impostazioni del piano
    async function savePianoSettings() {
        const newPianoSettings = {
            piano: {
                transpose: parseInt(inputTranspose.value),
                noteoffset: parseInt(inputNoteOffset.value),
                piano_white_note_size: parseFloat(inputPianoWhiteNoteSize.value),
                piano_black_note_size: parseFloat(inputPianoBlackNoteSize.value),
                led_size: parseFloat(inputLedSize.value),
                led_number: parseInt(inputLedNumber.value),
                max_brightness: parseInt(inputMaxBrightness.value)
            }
        };
        try {
            const response = await fetch('/api/settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(newPianoSettings),
            });
            const result = await response.json();
            if (!response.ok) throw new Error(result.message);
            alert(result.message);
        } catch (error) {
            console.error('Errore:', error);
            alert('Impossibile salvare le impostazioni del piano: ' + error.message);
        }
    }
    
    // Salva le impostazioni dei pedali
    async function savePedalSettings() {
        const newPedalSettings = {
            pedals: {
                mode: inputPedalMode.value,
                animation_gpio: parseInt(inputPedalAnimation.value),
                color_gpio: parseInt(inputPedalColor.value)
            }
        };
        try {
            const response = await fetch('/api/settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(newPedalSettings),
            });
            const result = await response.json();
            if (!response.ok) throw new Error(result.message);
            alert(result.message);
        } catch (error) {
            console.error('Errore:', error);
            alert('Impossibile salvare le impostazioni dei pedali: ' + error.message);
        }
    }

    // Event Listeners per le impostazioni
    themeToggle.addEventListener('change', (e) => {
        const theme = e.target.checked ? 'light' : 'dark';
        applyTheme(theme);
        localStorage.setItem('theme', theme);
    });

    colorSwatches.forEach(swatch => {
        swatch.addEventListener('click', () => {
            const color = swatch.dataset.color;
            applyAccentColor(color);
            localStorage.setItem('accentColor', color);
        });
    });

    // Aggiorna il testo dell'interruttore per l'animazione
    document.querySelectorAll('.toggle-input').forEach(toggle => {
        toggle.addEventListener('change', (e) => {
            const toggleText = e.target.nextElementSibling.nextElementSibling;
            if (toggleText && toggleText.classList.contains('toggle-text')) {
                toggleText.textContent = e.target.checked ? 'Animato' : 'Fisso';
            }
        });
    });

    btnSaveHw.addEventListener('click', saveHardwareSettings);
    btnSavePiano.addEventListener('click', savePianoSettings);
    btnSavePedal.addEventListener('click', savePedalSettings);

    // Aggiorna i valori numerici accanto agli slider
    const sliders = document.querySelectorAll('input[type="range"]');
    sliders.forEach(slider => {
        const valueSpan = slider.nextElementSibling;
        slider.addEventListener('input', () => {
            if (valueSpan && valueSpan.classList.contains('value-display')) {
                valueSpan.textContent = slider.value;
            }
        });
    });

    // Carica tutto all'avvio
    loadAllSettings();
});