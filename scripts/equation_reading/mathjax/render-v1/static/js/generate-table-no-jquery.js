// Version of table generation script that uses built-in 
//   javascript DOM operatiors to build table rows

// Assumes latex_data.js has already been loaded, providing latex_source variable

const format_xml = require('xml-formatter');

function generateTable(table, data) {
  let i = 0;

  for (let element of data) {
	let row = table.insertRow();

	let cell = row.insertCell();
	cell.id = `tex_src_${i}`;
	let text = document.createTextNode(`${element["src"]}`);
	cell.appendChild(text);

	mml = `${element["mml"]}`;

	cell = row.insertCell();
	cell.id = `mml_img_${i}`;
	cell.innerHTML = mml;  // MathJax will render if appropriate content in innerHTML

	// xml-formatter options to display xml more compactly
	let mml_formatted = format_xml(mml, {
	  indentation: '  ',
	  collapseContent: true, 
	  lineSeparator: '\n'
	});

	cell = row.insertCell();
	cell.id = `mml_src_${i}`;
	div_tag = document.createElement('div');
	div_tag.setAttribute('class', 'pre');
	pre_tag = document.createElement('pre');
	pre_tag.textContent = mml_formatted;
	div_tag.appendChild(pre_tag);
	cell.appendChild(div_tag);

	i++;
  }
}

let table = document.querySelector("table");
// let table = $("#table");
generateTable(table, latex_source);
