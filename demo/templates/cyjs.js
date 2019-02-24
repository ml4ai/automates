        var computational_graph = cytoscape({
        container: document.getElementById('computational_graph'),
          elements: {{ scopeTree_elementsJSON | safe }},
          style: [
                  { selector: 'node',
                    style: { 
                        'label': 'data(label)',
                        'shape': 'data(shape)',
                        'background-color': 'white',
                        'border-color': 'data(color)',
                        'border-width': '3pt',
                        'font-family': 'PT Sans, sans-serif',
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
        var api = computational_graph.expandCollapse({
            fisheye: false, undoable: false
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
        computational_graph.nodes().forEach(function(ele){
          ele.scratch()._tippy = makeTippy(ele);
        });
        computational_graph.on('tap', 'node', function(evt){
          computational_graph.$(':selected').removeClass('selectedNode');
          var node = evt.target;
          node.toggleClass('selectedNode');
          if (!node.selected()){
            node.select();
            node.scratch()._tippy.show();
            MathJax.Hub.Queue(["Typeset",MathJax.Hub]);
          }
          else {
            node.toggleClass('selectedNode');
            node.deselect();
            node.scratch()._tippy.hide();
          }
        });
        var causal_analysis_graph = cytoscape({
        container: document.getElementById('causal_analysis_graph'),
          elements: {{ program_analysis_graph_elementsJSON | safe }},
          style: [
                  { selector: 'node',
                    style: { 
                        'label': 'data(label)',
                        'shape': 'data(shape)',
                        'background-color': 'white',
                        'border-color': 'data(color)',
                        'border-width': '3pt',
                        'font-family': 'PT Sans, sans-serif',
                        'width':'label',
                        'text-valign': 'data(textValign)',
                        'padding': 15,
                    } 
                  }, { 
                    selector: 'edge',
                    style: { 
                      'curve-style' : 'bezier',
                      'control-point-step-size': '70px',
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
        causal_analysis_graph.nodes().forEach(function(ele){
          ele.scratch()._tippy = makeTippy(ele);
        });
        causal_analysis_graph.on('tap', 'node', function(evt){
          causal_analysis_graph.$(':selected').removeClass('selectedNode');
          var node = evt.target;
          node.toggleClass('selectedNode');
          if (!node.selected()){
            node.select();
            node.scratch()._tippy.show();
            MathJax.Hub.Queue(["Typeset",MathJax.Hub]);
          }
          else {
            node.toggleClass('selectedNode');
            node.deselect();
            node.scratch()._tippy.hide();
          }
        });
