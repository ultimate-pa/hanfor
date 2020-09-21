// Stylesheets
require('../scss/custom.scss');
require('datatables.net-bs4/css/dataTables.bootstrap4.css');
require('datatables.net-select-bs4/css/select.bootstrap4.css');
require('jquery-ui/themes/base/all.css');
require('../css/bootstrap-tokenfield.css');
require('../css/tether.css');
require('../css/app.css');

// Dark theme switch.
function update_color_theme() {
  let theme_switch = $('#dark_theme_switch');
  const theme_is_dark =
    localStorage.getItem('color_mode') !== null &&
    localStorage.getItem('color_mode') === 'dark';

  if (theme_is_dark) {
    document.body.setAttribute('data-theme', 'dark');
    theme_switch.prop('checked', true);
  } else {
    document.body.removeAttribute('data-theme');
    theme_switch.prop('checked', false);
  }
}

$('#dark_theme_switch').on('change', function() {
  if ($(this).is(':checked')) {
    localStorage.setItem('color_mode', 'dark');
  } else {
    localStorage.setItem('color_mode', 'light');
    document.body.removeAttribute('data-theme');
  }
  update_color_theme();
});

window.addEventListener('load', function() {
  update_color_theme();
});
