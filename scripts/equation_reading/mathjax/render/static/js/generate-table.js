// Assumes data_path has already been defined (in render_mathjax_jquery.hmtl)

// Version of table generation script that uses jquery to construct table rows

const format_xml = require('xml-formatter');

// triggers when HTML document is ready for processing
$(document).ready(function(){

  let table = $("#table");
  let i = 0;

  /*
  // DOES NOT WORK...
  // load eqn_src from json in data_path
  var eqn_src = (function() {
    var json = null;
    $.ajax({
      'async': false,
      'global': false,
      'url': data_path,
      'dataType': "json",
      'success': function (data) {
        json = data;
      }
    });
    return json;
  })();
  */

  // console.log("after attempt to load");
  console.log(eqn_src);

  // For each latex source datum in data:
  //   generate a table row, with
  //     <td> for original latex source (as plain text)
  //     <td> for loading image of latex-rendered
  //     <td> that has innerHTML as raw mml -- available to be rendered by MathJax
  //     <td> that contains pre-formatted MathML
  for (let element of eqn_src) {

    console.log(`in loop... ${i}`);

    let row = $("<tr/>",{ class: "datum" });
    var cell = $("<td/>", { id: `tex_src_${i}`,
                            text: `${i}: ${element["src"]}` });
    row.append(cell);

    image_path = `${images_path}/${i}.${images_ext}`;
    cell = $("<td/>", { id: `tex_img_${i}` }).append(`<img src="${image_path}" alt="${image_path}" width="200">`);
    row.append(cell);
    
    mml = `${element["mml"]}`;
    
    cell = $("<td/>", { id: `mml_img_${i}` }).html(mml);
    row.append(cell);
    
    // xml-formatter options to display xml more compactly
	mml_formatted = format_xml(mml, {
	  indentation: '  ',
	  collapseContent: true, 
	  lineSeparator: '\n'
	});
	
	cell = $("<td>", { id: `mml_src_${i}` })
		.append($("<div>", { class: 'pre' })
			.append($("<pre>").text( mml_formatted )) );
    
    row.append(cell);
    
    table.append(row);
    
    i++;
  }

});
