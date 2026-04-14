const {io} = require("socket.io-client")

document.querySelectorAll('[data-bs-toggle="tab"]').forEach(btn => {
    btn.addEventListener("click", () => {
        document.querySelectorAll('[data-bs-toggle="tab"]').forEach(b => {
            b.classList.remove("active");
            b.setAttribute("aria-selected", "false");
        });
        document.querySelectorAll(".tab-pane").forEach(p => {
            p.classList.remove("show", "active");
        });
        btn.classList.add("active");
        btn.setAttribute("aria-selected", "true");
        document.querySelector(btn.dataset.bsTarget).classList.add("show", "active");
    });
});



$(document).ready(function () {

    // region Data handling from API

    let ai_data;
    window.appSocket = io("/ai_addon_data", {
      path: url_prefix + "/socket.io/"
    });

    window.appSocket.on('connect', () => console.log("Connected to AI Data WebSocket"));
    window.appSocket.on('disconnect', () => console.log("Disconnected from AI Data WebSocket"));

    window.appSocket.on('ai_update', (newData) => {
        console.log("AI Update received:", newData);
    });
});