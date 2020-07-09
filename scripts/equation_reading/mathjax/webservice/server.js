const express = require('express');
const mjAPI = require("mathjax-node");

// Initialize the express server
var app = express();

// Configure and start the MathJax API
mjAPI.config({
  MathJax: {
    loader: {load: ['input/tex']}
  }
});
mjAPI.start();

// Define a GET routine to process a Tex --> MML conversion request
app.get('/TeX2MML', function (req, res) {
  // Access the LaTeX source from the request object
  var tex_str = req.query.tex_src

  // Call the typeset promise to convert LaTEX to MathML
  mjAPI.typeset({
    math: tex_str,
    format: "TeX",
    mml:true,
  }, function (data) {
    // Return the MathML produced by the LaTeX
    if (!data.errors) {
      res.end( JSON.stringify(data.mml));
    } else {
      res.end("An error occurred");
    }
  });
});

// Start the express application server
var server = app.listen(8081, function () {
   var port = server.address().port
   console.log("MathJax server listening at http://localhost:%s", port)
});
