// const format_xml = require('xml-formatter');


/**
 * Used to send MathML back to Python (returns something from Python for now, but not really necessary)
 * @return {[type]} [description]
 */
$(function() {
    $( 'a#process_input' ).bind('click', function() {
        var latex_source = $("#latex_source").text();
        MathJax.tex2mmlPromise(latex_source).then(function (mml) {  // , {display: display.checked}
            $.getJSON('/send_mml', {
                latex_source: mml
            }, function(data) {
                $("#result").text(data.result);
            });
        });
        return false;
    });
});


$(function() {
  $( 'a#tex_loader' ).bind('click', function() {
      $.ajax({
        url: '/latex2mml',
        data: {},
        type: 'GET',
        success: function(data) {
          var latex_str = data.latex;
          MathJax.tex2mmlPromise(latex_str).then(function (mml) {  // , {display: display.checked}
            $("#output").text(mml);
          });
        },
        error: function(error) {
            console.log(error);
        }
      });
  });
})
