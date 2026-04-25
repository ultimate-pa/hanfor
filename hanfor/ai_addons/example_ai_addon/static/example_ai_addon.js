const TAB_ID = "ai_addons_example_ai_addon";
const ADDON_NAME = "example-ai-addon"

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
    await window.post(ADDON_NAME, window.appSocket.id);
});

window.tabSubs.onDeactivate(TAB_ID, async () => {
    await window.del(ADDON_NAME, window.appSocket.id);
});


// -------------------------------------------------------------------------
// Buttons
// -------------------------------------------------------------------------

document.getElementById("btn-private").addEventListener("click", async () => {
    await window.post(ADDON_NAME, "increment-client-counter/" + window.appSocket.id);
});

document.getElementById("btn-global").addEventListener("click", async () => {
    await window.post(ADDON_NAME, "increment-global-counter");
});