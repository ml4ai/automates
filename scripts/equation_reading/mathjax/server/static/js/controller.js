// const format_xml = require('xml-formatter');

function convert() {
    //
    //  Get the TeX input
    //
    var latex_source = $("#latex_source").text();
    //
    //  Clear the old output
    //
    var output = $("#output")
    output.html('<pre></pre>')
    //
    //  Reset the tex labels (and automatic equation numbers, though there aren't any here).
    //  Convert the input to MathML output and use a promise to wait for it to be ready
    //    (in case an extension needs to be loaded dynamically).
    //
    MathJax.texReset();
    MathJax.tex2mmlPromise(latex_source).then(function (mml) {  // , {display: display.checked}
        //
        //  The promise returns the serialized MathML, and we add that
        //  to the <pre> element in the output.
        //

        // xml-formatter options to display xml more compactly
        // doesn't work?
        /*
        let mml_formatted = format_xml(mml, {
            indentation: '  ',
            collapseContent: true,
            lineSeparator: '\n'
        });
        */

        output.text(mml)
    });

    /*
    .catch(function (err) {
        //
        //  If there was an error, put the message into the output instead
        //
        //output.firstChild.appendChild(document.createTextNode(err.message));
        output.text(err.message)
    }).then(function () {
        //
        //  Error or not, re-enable the display and render buttons
        //
        //button.disabled = display.disabled = false;
    });
    */
}


$(function() {
    $( 'a#process_input' ).bind('click', function() {

        convert();

        console.log($("#output"));

        $.getJSON('/latex_to_mml', {
            latex_source: $("#output").val()
        }, function(data) {
            $("#result").text(data.result);
        });

        /*
        $.getJSON('/background_process', {
            proglang: $('input[name="proglang"]').val(),
        }, function(data) {
            $("#result").text(data.result);
        });
        */

        return false;
    });
});