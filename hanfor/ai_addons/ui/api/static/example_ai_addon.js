const TAB_ID = "ai_addons_example_ai_addon";

// -------------------------------------------------------------------------
// Socket - receives counter updates from the backend
// -------------------------------------------------------------------------

window.tabSubs.register(TAB_ID, [
    {
        event: "socket_example_counter",
        handler: (data) => {
            if (data.scope === "private") {
                document.getElementById("private-counter").textContent = data.counter;
            } else {
                document.getElementById("global-counter").textContent = data.counter;
            }
        },
    },
]);

// -------------------------------------------------------------------------
// Lifecycle - register sid when tab becomes active, clear on leave
// -------------------------------------------------------------------------

window.tabSubs.onActivate(TAB_ID, async () => {
    await fetch(`${window.baseUrl}/example-ai-addon/${window.appSocket.id}`, { method: "POST" });
});

window.tabSubs.onDeactivate(TAB_ID, async () => {
    await fetch(`${window.baseUrl}/example-ai-addon/${window.appSocket.id}`, { method: "DELETE" });
});


// -------------------------------------------------------------------------
// Buttons
// -------------------------------------------------------------------------

document.getElementById("btn-private").addEventListener("click", async () => {
    await fetch(`${window.baseUrl}/example-ai-addon/increment-client-counter/${window.appSocket.id}`, { method: "POST" });
});

document.getElementById("btn-global").addEventListener("click", async () => {
    await fetch(`${window.baseUrl}/example-ai-addon/increment-global-counter`, { method: "POST" });
});