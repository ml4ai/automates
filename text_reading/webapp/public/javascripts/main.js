var bratLocation = 'assets/brat';

// Color names used
var baseConceptColor = '#CCD1D1';
var causalEventColor = '#BB8FCE';



head.js(
    // External libraries
    bratLocation + '/client/lib/jquery.min.js',
    bratLocation + '/client/lib/jquery.svg.min.js',
    bratLocation + '/client/lib/jquery.svgdom.min.js',

    // brat helper modules
    bratLocation + '/client/src/configuration.js',
    bratLocation + '/client/src/util.js',
    bratLocation + '/client/src/annotation_log.js',
    bratLocation + '/client/lib/webfont.js',

    // brat modules
    bratLocation + '/client/src/dispatcher.js',
    bratLocation + '/client/src/url_monitor.js',
    bratLocation + '/client/src/visualizer.js'
);

var webFontURLs = [
    bratLocation + '/static/fonts/Astloch-Bold.ttf',
    bratLocation + '/static/fonts/PT_Sans-Caption-Web-Regular.ttf',
    bratLocation + '/static/fonts/Liberation_Sans-Regular.ttf'
];

var collData = {
    entity_types: [ {
        "type"   : "Concept",
        "labels" : ["Concept"],
        // Blue is a nice colour for a person?
        "bgColor": baseConceptColor,
        // Use a slightly darker version of the bgColor for the border
        "borderColor": "darken"
    }
    ],
//    relation_types: [{
//                         type     : 'Note',
//                         labels   : ['Note', 'NOTE'],
//                         // dashArray allows you to adjust the style of the relation arc
//                         //dashArray: '3,3',
//                         color    : '#ceb1db',
//                         /* A relation takes two arguments, both are named and can be constrained
//                             as to which types they may apply to */
//                         args     : [
//                             //
//                             {role: 'Specifier', targets: ['Spec'] },
//                             {role: 'Entity',  targets: ['Person'] }
//                         ]
//                     }],

    event_types: [
      {
        "type": "Causal",
        "labels": ["CAUSE"],
        "bgColor": causalEventColor,
        "borderColor": "darken",
        "arcs": [
            {"type": "agent", "labels": ["agent"], "borderColor": "darken", "bgColor":"violet"},
            {"type": "theme", "labels": ["theme"], "borderColor": "darken", "bgColor":"violet"}
        ]
      }
    ]
};

// docData is initially empty.
var docData = {};

head.ready(function() {

    var syntaxLiveDispatcher = Util.embed('syntax',
        $.extend({'collection': null}, collData),
        $.extend({}, docData),
        webFontURLs
    );
    var eidosMentionsLiveDispatcher = Util.embed('eidosMentions',
        $.extend({'collection': null}, collData),
        $.extend({}, docData),
        webFontURLs
    );

    $('form').submit(function (event) {

        // stop the form from submitting the normal way and refreshing the page
        event.preventDefault();

        // collect form data
        var formData = {
            'sent': $('textarea[name=text]').val(),
            'showEverything': $('input[name=showEverything]').is(':checked')
        }

        if (!formData.sent.trim()) {
            alert("Please write something.");
            return;
        }

        // show spinner
        document.getElementById("overlay").style.display = "block";

        // process the form
        $.ajax({
            type: 'GET',
            url: 'parseSentence',
            data: formData,
            dataType: 'json',
            encode: true
        })
        .fail(function () {
            // hide spinner
            document.getElementById("overlay").style.display = "none";
            alert("error");
        })
        .done(function (data) {
            console.log(data);
            syntaxLiveDispatcher.post('requestRenderData', [$.extend({}, data.syntax)]);
            eidosMentionsLiveDispatcher.post('requestRenderData', [$.extend({}, data.eidosMentions)]);
            document.getElementById("groundedAdj").innerHTML = data.groundedAdj;
            document.getElementById("parse").innerHTML = data.parse;
            // hide spinner
            document.getElementById("overlay").style.display = "none";
        });

    });
});
