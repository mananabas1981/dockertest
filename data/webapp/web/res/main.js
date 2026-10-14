

import app_init from './app/main.js';

window.onload = function () {
  app_init();
  setTimeout(function () {
    document.querySelector('#style').remove();
    document.querySelector('#top-loader').remove();
    document.querySelector('.pos-spin').remove();
    document.querySelector('#module').remove();
  }, 1000);
}