/**
 * ScanFlow AI – Frontend-Logik.
 *
 * Aktualisiert die Status-Karten auf dem Dashboard automatisch.
 */

(function () {
    "use strict";

    function updateStatus() {
        fetch("/api/status")
            .then(function (r) { return r.json(); })
            .then(function (data) {
                var el;
                el = document.getElementById("inboxCount");
                if (el) el.textContent = data.inbox_files;

                el = document.getElementById("outputCount");
                if (el) el.textContent = data.output_files;

                el = document.getElementById("nasStatus");
                if (el) {
                    el.textContent = data.nas_mounted ? "Verbunden" : "Getrennt";
                    el.style.color = data.nas_mounted ? "var(--success)" : "var(--error)";
                }

                el = document.getElementById("apiStatus");
                if (el) {
                    el.textContent = data.api_key_set ? "Gesetzt" : "Fehlt";
                    el.style.color = data.api_key_set ? "var(--success)" : "var(--error)";
                }
            })
            .catch(function () {
                /* Stille Fehlerbehandlung – nächster Versuch in 10s */
            });
    }

    if (document.getElementById("statusCards")) {
        updateStatus();
        setInterval(updateStatus, 10000);
    }
})();
