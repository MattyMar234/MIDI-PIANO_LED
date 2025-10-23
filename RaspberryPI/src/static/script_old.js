document.addEventListener('DOMContentLoaded', () => {
    const navButtons = document.querySelectorAll('.nav-button');
    const panels = document.querySelectorAll('.control-panel');
    const activateButtons = document.querySelectorAll('.btn-activate');
    const btnSpegni = document.getElementById('btn-spegni-tutto');

    // --- Funzione per inviare comandi al backend ---
    async function sendCommand(payload) {
        try {
            const response = await fetch('/api/control', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            const result = await response.json();
            if (!response.ok) {
                throw new Error(result.message || 'Errore nel comando');
            }
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

    // Aggiungi event listener ai bottoni della sidebar
    navButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetId = button.dataset.target;
            switchPanel(targetId);
        });
    });

    // --- Gestore per il pulsante "Spegni Tutto" ---
    btnSpegni.addEventListener('click', () => {
        sendCommand({ modalita: 'spegni' });
    });

    // --- Gestori per i pulsanti "Applica" di ogni modalità ---
    activateButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            // Trova il pannello genitore del bottone cliccato
            const panel = e.target.closest('.control-panel');
            const mode = panel.id;
            let payload = { modalita: mode };

            // Raccoglie i dati solo dal pannello corrente
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

    // --- Aggiorna i valori numerici accanto agli slider ---
    const sliders = document.querySelectorAll('input[type="range"]');
    sliders.forEach(slider => {
        const valueSpan = slider.nextElementSibling; // Assume che lo span sia il fratello successivo
        slider.addEventListener('input', () => {
            if (valueSpan && valueSpan.classList.contains('value-display')) {
                valueSpan.textContent = slider.value;
            }
        });
    });
});