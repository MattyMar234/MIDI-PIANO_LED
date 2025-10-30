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
    const inputLedCount = document.getElementById('setting-led-count');
    const inputLedPin = document.getElementById('setting-led-pin');

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
        if (button.id === 'btn-save-hw-settings') return; // Esclude il bottone di salvataggio HW
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
                payload.luminosita = parseInt(panel.querySelector('#luminosita-schema').value);
                payload.durata = parseInt(panel.querySelector('#durata-schema').value);
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
            alert('Impossibile salvare le impostazioni: ' + error.message);
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

    btnSaveHw.addEventListener('click', saveHardwareSettings);

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