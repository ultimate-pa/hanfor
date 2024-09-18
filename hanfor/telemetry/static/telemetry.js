const {io} = require("socket.io-client")
const {v4: uuidv4} = require("uuid")

exports.sendTelemetry = sendTelemetry

let socket = io("/telemetry");

socket.on('connect', function () {
    console.log('connect');
});
socket.on('disconnect', function () {
    console.log('disconnect');
});

socket.on('command', function (msg) {
    console.log("command: " + msg);
    if (msg === "send_user_id") {
        let userid = getCookie("userid")
        if (userid === "") {
            userid = uuidv4()
            setCookie("userid", userid, 365)
        }
        socket.emit("user_id", userid)
    } else if (msg === "no_telemetry") {
        console.log("Telemetry disabled")
    }
});

function sendTelemetry(scope, id, event) {
    let msg = {
        "scope": scope,
        "id": id,
        "event": event
    }
    socket.emit("event", JSON.stringify(msg))
}

function setCookie(c_name, c_value, ex_days) {
    const d = new Date();
    d.setTime(d.getTime() + (ex_days * 24 * 60 * 60 * 1000));
    let expires = "expires=" + d.toUTCString();
    document.cookie = c_name + "=" + c_value + ";" + expires + ";path=/";
}

function getCookie(cname) {
    let name = cname + "=";
    let decodedCookie = decodeURIComponent(document.cookie);
    let ca = decodedCookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) === 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}