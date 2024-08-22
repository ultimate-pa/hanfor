const { io } = require("socket.io-client")
const { v4: uuidv4 } = require("uuid")

let socket = io("/telemetry");

socket.on('connect', function () {
    let userid = getCookie("userid")
    if (userid === "") {
        userid = uuidv4()
        setCookie("userid", userid, 365)
    }
    socket.emit("userid", userid)
    console.log('connect');
});
socket.on('disconnect', function () {
    console.log('disconnect');
});

let socket2 = io("/telemetry2");
socket2.on('connect', function () {
    console.log('connect2');
});
socket2.on('disconnect', function () {
    console.log('disconnect2');
});

socket.on('my_connect', function (msg) {
    console.log(msg);
});

$(document).ready(function () {
    // sending a connect request to the server.

});

function setCookie(c_name, c_value, ex_days) {
  const d = new Date();
  d.setTime(d.getTime() + (ex_days*24*60*60*1000));
  let expires = "expires="+ d.toUTCString();
  document.cookie = c_name + "=" + c_value + ";" + expires + ";path=/";
}

function getCookie(cname) {
  let name = cname + "=";
  let decodedCookie = decodeURIComponent(document.cookie);
  let ca = decodedCookie.split(';');
  for(let i = 0; i <ca.length; i++) {
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