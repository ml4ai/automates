const xml_formatter = require('xml-formatter');

MathJax = {
//
//  Load only TeX input and the contextual menu
//
loader: {load: ['input/tex', 'ui/menu']},
//
startup: {
  ready() {
	MathJax.startup.defaultReady();
	MathJax.startup.document.menu.menu.findID('Accessibility', 'AssistiveMml').disable();
  },
  pageReady() {
	MathJax._.mathjax.mathjax.handleRetriesFor(() => {
	  MathJax.startup.document.render();
	});
  }
},
//
//  Use dollar signs for in-line delimiters in addition to the usual ones
//
tex: {inlineMath: {'[+]': [['$', '$']]}},
//
//  Override the usual typeset render action with one that generates MathML output
//
options: {
  menuOptions: {
	settings: {
	  assistiveMml: false
	}
  },

  renderActions: {
	typeset: [150,
	  //
	  //  The function for rendering a document's math elements
	  //
	  (doc) => {
	  
		let i = 0;
		for (math of doc.math) {
		
		  console.log(math);
		
		  latex_src_elm = document.getElementById(`tex_src_${i}`);
		  latex_src_string = latex_src_elm.textContent;

		  // extract just the src, not the enclosing mathjax latex indicators
		  latex_src = latex_src_string.substring(2, latex_src_string.length-2);

		  // console.log(latex_src_elm);
		  // console.log(latex_src);
		
		  mml = MathJax.startup.toMML(math.root);
		  
		  mml_img = document.getElementById(`mml_img_${i}`);
		  mml_img.innerHTML = mml;
		  
		  console.log(xml_formatter(mml));
		  
		  mml_src = document.getElementById(`mml_src_${i}`);
		  mml_src.textContent = mml;  // pretty-print xml using xml-formatter
		
		  // console.log(latex_src_elm);
		  
		  // The commented line 86 restores the latex src text to the elm
		  // However, results in the following error:
		  //     TypeError: this.parent(...) is null - in core.js:1:59028
		  //latex_src_elm.textContent = latex_src;
		  
		  latex_src_elm.appendChild(document.createTextNode(latex_src));
		
		  // The next line is from the original mathjax web demo script
		  //     if remove next line, get the following error:
		  //        TypeError: t is null - in menu.js:1:24458
		  //     if keep next line, will remove the latex source in the first table cell
		  math.typesetRoot = document.createElement('mjx-container');
		  
		  // from original mathjax web demo script
		  // math.typesetRoot.innerHTML = mml;
		  // math.display && math.typesetRoot.setAttribute('display', 'block');
		  
		  // console.log(i);
		  
		  i++;
		}
		
	  }
	  
	]
  } // end renderActions

}
};