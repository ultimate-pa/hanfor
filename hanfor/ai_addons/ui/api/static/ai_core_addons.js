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
    window.appSocket = io("/ai_addon_data", {
        path: url_prefix + "/socket.io/"
    });

    window.appSocket.on('connect', () => console.log("Connected to AI Data WebSocket"));
    window.appSocket.on('disconnect', () => console.log("Disconnected from AI Data WebSocket"));

    window.appSocket.on('reload', () => {
        if (document.getElementById('reload-banner')) return;

        const banner = document.createElement('div');
        banner.id = 'reload-banner';
        banner.innerHTML = `
            Configuration changed. 
            <a href="#" onclick="location.reload()">Reload now</a> to apply updates.
        `;
        banner.className = 'alert alert-warning alert-dismissible m-2';
        document.querySelector('main').prepend(banner);
    });
});