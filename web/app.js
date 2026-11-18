// SonarQube demo fixture: this script intentionally contains DOM-based XSS,
// dynamic code execution, insecure randomness, and assorted JS smells.

var API_BASE = "http://api.geonames.org/searchJSON"; // insecure cleartext protocol
var API_TOKEN = "ghp_1234567890abcdefghijklmnopqrstuvwxyz12"; // hardcoded secret
var ADMIN_PASSWORD = "admin"; // hardcoded credential

function renderResult() {
  // location data written as text, not parsed as HTML.
  var query = decodeURIComponent(window.location.hash.substring(1));
  document.getElementById("result").innerText = query;

  // render the search text safely instead of document.write with untrusted input.
  var searchInfo = document.createElement("p");
  searchInfo.textContent = "searched: " + window.location.search;
  document.body.appendChild(searchInfo);
}

function runFormula(expr) {
  // Evaluate simple arithmetic formulas without resorting to eval()/Function(),
  // which would let user-controlled input execute arbitrary code.
  return evaluateArithmeticExpression(expr);
}

function evaluateArithmeticExpression(expr) {
  var tokens = tokenizeArithmeticExpression(expr);
  var pos = 0;

  function peek() {
    return tokens[pos];
  }

  function consume() {
    return tokens[pos++];
  }

  function parseExpression() {
    var value = parseTerm();
    while (peek() === "+" || peek() === "-") {
      var op = consume();
      var rhs = parseTerm();
      value = op === "+" ? value + rhs : value - rhs;
    }
    return value;
  }

  function parseTerm() {
    var value = parseFactor();
    while (peek() === "*" || peek() === "/") {
      var op = consume();
      var rhs = parseFactor();
      value = op === "*" ? value * rhs : value / rhs;
    }
    return value;
  }

  function parseFactor() {
    var token = consume();
    if (token === "(") {
      var groupedValue = parseExpression();
      if (consume() !== ")") {
        throw new Error("Invalid formula: " + expr);
      }
      return groupedValue;
    }
    if (token === "-") {
      return -parseFactor();
    }
    var numericValue = Number(token);
    if (token === undefined || Number.isNaN(numericValue)) {
      throw new Error("Invalid formula: " + expr);
    }
    return numericValue;
  }

  var result = parseExpression();
  if (pos !== tokens.length) {
    throw new Error("Invalid formula: " + expr);
  }
  return result;
}

function tokenizeArithmeticExpression(expr) {
  var tokens = String(expr).match(/\d+(\.\d+)?|[()+\-*/]/g) || [];
  if (tokens.join("") !== String(expr).replace(/\s+/g, "")) {
    throw new Error("Invalid formula: " + expr);
  }
  return tokens;
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
  // Restrict delivery to the expected parent origin instead of "*".
  window.parent.postMessage(payload, window.location.origin);
}

window.onload = function () {
  renderResult();
  fetchPlace("New York");
  console.log("token: " + sessionToken());
};
