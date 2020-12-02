// Assumes eqn_src has already been defined 
// (loaded from latex_data_dev.js in render_equations.html)

// Version of table generation script that uses jquery to construct table rows

const format_xml = require('xml-formatter');

function build_table() {

  let table = $("#table");
  //let i = 0;

  // For each latex source datum in data:
  //   generate a table row, with
  //     <td> for original latex source (as plain text)
  //     <td> for loading image of latex-rendered
  //     <td> that has innerHTML as raw mml -- available to be rendered by MathJax
  //     <td> that contains pre-formatted MathML
  for (let element of eqn_src) {

    let i = element["eqn_num"];
    //console.log(i);

    let row = $("<tr/>",{ class: "datum" });
    var cell = $("<td/>", { id: `tex_src_${i}`,
                            text: `${i}: ${element["src"]}` });
    row.append(cell);

    image_path = `${images_path}/${i}.${images_ext}`;
    // image_path = `../${images_path}/${i}.${images_ext}`;
    // image_path = `\{\{ url_for('static', filename='${images_path}/${i}.${images_ext}') \}\}`;
    cell = $("<td/>", { id: `tex_img_${i}` }).append(`<img src="${image_path}" alt="${image_path}" width="200">`);
    row.append(cell);

    mml = `${element["mml"]}`;

    cell = $("<td/>", { id: `mml_img_${i}` }).html(mml);
    row.append(cell);

    // xml-formatter options to display xml more compactly
//    mml_formatted = mml
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
}


// triggers when HTML document is ready for processing
$(document).ready(function() {

  // load eqn_src from json in data_path
  /*
  $.getJSON('/load_data',
    { filepath: data_path },  // data_path defined in templates/index.html
    function (data) {
      build_table(data);
    });
  */
  
  build_table();

});
