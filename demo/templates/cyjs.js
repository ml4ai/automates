        var cy = cytoscape({
        container: document.getElementById('cy'),
          elements: {{ elementsJSON | safe }},
          style: [
                  { selector: 'node',
                    style: { 
                        'label': 'data(label)',
                        'shape': 'data(shape)',
                        'background-color': 'white',
                        'border-color': 'data(color)',
                        'border-width': '3pt',
                        'font-family': 'Menlo, monospace',
                        'width':'label',
                        'text-valign': 'data(textValign)',
                        'padding': 15,
                    } 
                  }, { 
                    selector: 'edge',
                    style: { 
                      'curve-style' : 'bezier',
                      'target-arrow-shape': 'triangle',
                    } 
                  }, { 
                    selector: '.selectedNode',
                    style: { 
                      'background-color': '#d3d3d3',
                    } 
                  }
              ],
          layout: { name: 'dagre' , rankDir: 'TB'},
          maxZoom : 10,
          minZoom : 0.1,
          selectionType: 'single'
        });

        var makeTippy = function(node){
            return tippy(node.popperRef(), {
                html: (function(){
                    var div = document.createElement('div');
                    div.innerHTML = node.data('tooltip');
                    return div;
                })(),
                trigger: 'manual',
                arrow: true,
                placement: 'bottom',
                hideOnClick: 'toggle',
                multiple: true,
                sticky: true
            } ).tooltips[0];
        };
        cy.nodes().forEach(function(ele){
          ele.scratch()._tippy = makeTippy(ele);
        });
        cy.on('tap', 'node', function(evt){
          cy.$(':selected').removeClass('selectedNode');
          var node = evt.target;
          node.toggleClass('selectedNode');
          if (!node.selected()){
            node.select();
            node.scratch()._tippy.show();
            MathJax.Hub.Queue(["Typeset",MathJax.Hub]);
          }
          else {
            node.deselect();
            node.scratch()._tippy.hide();
          }
        });

