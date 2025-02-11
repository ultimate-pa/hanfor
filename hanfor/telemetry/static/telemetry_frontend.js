import {getCookie, setCookie} from "./cookie_control"

$(document).ready(function () {
      // Set the current name initially
      $('#currentName').text(getCookie("userid"));

      // Handle form submission
      $('#nameForm').on('submit', function (event) {
        event.preventDefault(); // Prevent default form submission
        const newName = $('#newName').val();

        if (newName.trim() === "") {
          $('#result').html('<div class="alert alert-danger">Please enter a new name.</div>');
        } else {
            setCookie("userid", newName.trim(), 365)
          $('#result').html(`<div class="alert alert-success">Name updated successfully! New Name: ${newName}</div>`);
        }
      });
    });
