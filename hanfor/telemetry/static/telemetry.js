const {io} = require("socket.io-client")
const {v4: uuidv4} = require("uuid")
import {getCookie, setCookie} from "./cookie_control"

let socket = io("/telemetry",{
  path: url_prefix + "/socket.io/"
});

socket.on('connect', function () {
    console.log('connect');
});
socket.on('disconnect', function () {
    console.log('disconnect');
});

socket.on('command', function (msg) {
    console.log("command: " + msg);
    if (msg === "send_user_info") {
        let userid = getCookie("userid")
        if (userid === "") {
            userid = uuidv4()
            setCookie("userid", userid, 365)
        }
        socket.emit("user_info", {"user_id": userid, "path": window.location.pathname})
    } else if (msg === "no_telemetry") {
        console.log("Telemetry disabled")
    }
});

export function sendTelemetry(scope, id, event) {
    let msg = {
        "scope": scope,
        "id": id,
        "event": event
    }
   socket.emit("event", JSON.stringify(msg))
}
