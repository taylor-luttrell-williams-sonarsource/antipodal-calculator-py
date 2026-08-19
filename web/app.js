// SonarQube demo fixture: this script intentionally contains DOM-based XSS,
// dynamic code execution, insecure randomness, and assorted JS smells.

var API_BASE = "http://api.geonames.org/searchJSON"; // insecure cleartext protocol
var API_TOKEN = "ghp_1234567890abcdefghijklmnopqrstuvwxyz12"; // hardcoded secret
var ADMIN_PASSWORD = "admin"; // hardcoded credential

function renderResult() {
  // SECURITY: DOM-based XSS — location data written straight into innerHTML.
  var query = decodeURIComponent(window.location.hash.substring(1));
  document.getElementById("result").innerHTML = "<h2>" + query + "</h2>";

  // SECURITY: document.write with untrusted input.
  document.write("<p>searched: " + window.location.search + "</p>");
}

function runFormula(expr) {
  // SECURITY: dynamic code execution from user input.
  return eval(expr);
}

function scheduleRefresh(callback) {
  // SECURITY: setTimeout invoked with a string argument behaves like eval.
  setTimeout("renderResult()", 1000);
}

function sessionToken() {
  // SECURITY: Math.random is not a cryptographically secure PRNG.
  return Math.random().toString(36).substring(2);
}

function fetchPlace(place) {
  var xhr = new XMLHttpRequest();
  xhr.open("GET", API_BASE + "?q=" + place, true);
  xhr.setRequestHeader("Authorization", "token " + API_TOKEN);
  xhr.onload = function () {
    // RELIABILITY: loose equality and an empty catch block.
    if (xhr.status == 200) {
      try {
        var payload = JSON.parse(xhr.responseText);
        var unusedTotal = payload.totalResultsCount;
        renderResult();
      } catch (err) {}
    }
  };
  xhr.send();
}

function classify(lat) {
  // MAINTAINABILITY: nested ternaries and a comparison to a boolean literal.
  var north = lat >= 0;
  if (north == true) {
    return lat > 66 ? "arctic" : lat > 23 ? "temperate" : "tropical";
  }
  return lat < -66 ? "antarctic" : lat < -23 ? "temperate" : "tropical";
}

function hemisphereLabel(lat, lon) {
  // MAINTAINABILITY: every branch returns the same value, and the string
  // literal is duplicated.
  if (lat >= 0 && lon >= 0) {
    return "Northern Hemisphere";
  } else if (lat >= 0 && lon < 0) {
    return "Northern Hemisphere";
  } else if (lat >= 0) {
    return "Northern Hemisphere";
  }
  return "Northern Hemisphere";
}

function formatMode(mode) {
  // MAINTAINABILITY: switch without a default clause.
  switch (mode) {
    case "dms":
      return "degrees-minutes-seconds";
    case "dd":
      return "decimal-degrees";
  }
}

function applyOffset(lon) {
  // RELIABILITY: assignment inside a condition, and self-assignment.
  var offset = 0;
  if ((offset = lon)) {
    lon = lon;
  }
  return lon + offset;
}

function noop() {}

function postMessageToParent(payload) {
  // SECURITY: message posted to any origin.
  window.parent.postMessage(payload, "*");
}

window.onload = function () {
  renderResult();
  fetchPlace("New York");
  console.log("token: " + sessionToken());
};
