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
    await fetch("/ai_addons/example_ai_addon/set_sid", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({sid: window.appSocket.id }),
    });
});

window.tabSubs.onDeactivate(TAB_ID, async () => {
    await fetch("/ai_addons/example_ai_addon/clear_sid", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({sid: window.appSocket.id }),
    });
});



// -------------------------------------------------------------------------
// Buttons
// -------------------------------------------------------------------------

document.getElementById("btn-private").addEventListener("click", async () => {
    console.log("btn-private")
    await fetch("/ai_addons/example_ai_addon/increment_for_client", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({sid: window.appSocket.id }),
    });
});

document.getElementById("btn-global").addEventListener("click", async () => {
    console.log("btn-global")
    await fetch("/ai_addons/example_ai_addon/increment_for_all", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
    });
});