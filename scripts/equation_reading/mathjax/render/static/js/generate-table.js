// Assumes latex_data.js has already been loaded, providing latex_source variable

// Version of table generation script that uses jquery to construct table rows

const format_xml = require('xml-formatter');

// triggers when HTML document is ready for processing
$(document).ready(function(){

  let table = $("#table");
  let i = 0;

  // For each latex source datum in latex_source:
  //   generate a table row, with
  //     <td> for original latex source (as plain text)
  //     <td> that has innerHTML as raw mml -- available to be rendered by MathJax
  //     <td> that contains pre-formatted MathML
  for (let element of latex_source) {
    let row = $("<tr/>",{ class: "datum" });
    var cell = $("<td/>", { id: `tex_src_${i}`,
                            text: `${element["src"]}` });
    row.append(cell);
    
    mml = `${element["mml"]}`;
    
    cell = $("<td/>", { id: `mml_img_${i}` }).html(mml);
    row.append(cell);
    
    // xml-formatter options to display xml more compactly
	let mml_formatted = format_xml(mml, {
	  indentation: '  ',
	  collapseContent: true, 
	  lineSeparator: '\n'
	});
	
	cell = $("<td>", { id: `mml_src_${i}` })
		.append($("<div>", { class: 'pre' })
			.append($("<pre>").text( mml_formatted )) );
    
    row.append(cell);
    
    table.append(row)
    
    i++;
  }

});
