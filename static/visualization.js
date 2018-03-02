/**
 * Created by ivania on 04-05-16.
 */

function changeMethod() {
    var loader = document.getElementById("loading-transform");
    loader.style.display = "inline";
    //Obtenemos el tipo de transformación. Por ahora solo servirá para saber cuál mostrar
    var transform_selector = document.getElementById("transform_selector");
    var transform = transform_selector.options[transform_selector.selectedIndex].value;
    ga('send', 'event', 'Visualization', 'DimensionalityReduction', "ChangeTo{0}".format(transform), {
        dimension2: new Date().getTime()
    });
    var ids = [];
    var classes = [];
    for (var doc in datum) {
        ids.push(doc);
        classes.push(datum[doc].relevance)
    }
    if ((transform == 'lda' && classes.indexOf(1) >= 0 && classes.indexOf(0) >= 0 && classes.indexOf(-1) >= 0) || transform != "lda") {
        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", "/change_transformation/{0}/{1}".format(user_id, transform), true);
        xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
        xhttp.send(JSON.stringify({
            ids: ids,
            classes: classes
        }));
        xhttp.onreadystatechange = function () {
            if (xhttp.readyState == 4 && xhttp.status == 200) {
                var data = JSON.parse(xhttp.responseText)
                var document_set = data["documents"]
                // Aquí solo hay que actualizar las posiciones
                document_set.forEach(function (e) {
                    var doc = datum[e.id];
                    doc['x'] = e.x;
                    doc['y'] = e.y;
                });
                var documents = getValues(datum);
                removeContentFrom("vis-svg");
                loadVisDocs(documents, "vis", filter_primary, filter_systematic)
                loader.style.display = 'none'
            }
            else {
                console.log('Problema en server')
            }
        };
    }
    else {
        alert("Esta transformación no se puede realizar. Intenta otra")
        loader.style.display = "none"
    }
}
function zoom() {
    scaleFactor = d3.event.scale;
    translation = d3.event.translate;
    tick(); //update positions
}
var last_zoom = null
var last_zoom_time = new Date().getTime()
function loadVisDocs(data, container, filter_primary, filter_systematic) {
    var svg_container = document.querySelector("#" + container + " svg");
    var width = svg_container.width['baseVal']["value"];
    var height = svg_container.height['baseVal']["value"] - 34; // Menos la altura de los botones de la visualización
    var aux = getScale(data, width, height)
    scaleX = aux[0];
    scaleY = aux[1];
    var zoomer = d3.behavior.zoom()
        .scaleExtent([0.1, 20])
        //allow 10 times zoom in or out
        .on("zoom", zoom)
        .on("zoomend", function () {
            var eventValue;
            if (lastScaleFactor > scaleFactor) {
                eventValue = "Out"
            } else {
                eventValue = "In"
            }
            lastScaleFactor = scaleFactor
            if (!last_zoom){
                last_zoom = eventValue
            }
            var time_zoom = new Date().getTime()
            if (last_zoom != eventValue && last_zoom_time < time_zoom - 5000 ){
                ga('send', 'event', 'Visualization', 'Zoom', eventValue, lastScaleFactor, {
                    dimension2: time_zoom
                });
                last_zoom = eventValue
                last_zoom_time = time_zoom
            }
        })
        .x(scaleX)
        .y(scaleY);
    var zoom_area = svg.append("g")
        .attr("id", "plot")
        .call(zoomer); //Attach zoom behaviour.
    var rect = zoom_area.append("rect")
        .attr("width", width)
        .attr("height", height)
        .style("fill", "none")
        .style("pointer-events", "all");
    var systematic = data.filter(filter_primary)
    var primary = data.filter(filter_systematic)
    var vis = zoom_area.append("g")
        .attr("class", "plotting-area")
    var circle_container = vis.append("g").attr("class", "primary-studies")
    circles = circle_container.selectAll(".document")
        .data(primary)
        .enter()
        .append('circle')
        .attr("r", 10)
        .attr("cx", function (d) {
            return (scaleX(d.x));
        })
        .attr("cy", function (d) {
            return (scaleY(d.y));
        })
        .on("click", function(d){
            this.setAttribute("r", "15");
        })
        .attr("class", "document");
    //.onclick
    //circles.exit().remove();
    var rects_container = vis.append("g").attr("class", "systematic-reviews")
    rects = rects_container.selectAll(".document")
        .data(systematic)
        .enter()
        .append("rect")
        .attr("x", function (d) {
            return (scaleX(d.x));
        })
        .attr("y", function (d) {
            return (scaleY(d.y));
        })
        .attr("width", 12)
        .attr('height', 12)
        .on("click", function(d){
            this.setAttribute("width", "20");
            this.setAttribute("height", "20");
        })
        .attr("class", "document");

    //rects.exit().remove();
    svg.selectAll('.document')
        .style("opacity", function (d) {
            if (filter_primary(d) || filter_systematic(d)) {
                return 0.5
            } else {
                return 0.7
            }
        })
        .style("fill", function (d) {
            if (d.type == 'query') {
                return "#FFF"
            } else {
                return color(d.relevance);
            }
        })
        .attr("id", function (d) {
            return ("v-" + d.id);
        })
        .attr("data-id", function (d) {
            return d.id
        })
        .on("click", function (d) {
            // Agregar clase details a la viz
            removeInfoDetails();
            addInfoDetails(d)
            turnOffPanels();
            turnOffViz(svg)
            this.classList.add("active");
            if (this.tagName == "rect"){
                this.setAttribute("width", "20");
            this.setAttribute("height", "20");
            }else{
                this.setAttribute("r", "15");
            }
            lightUpPanels(panels, d.id)
            ga('send', 'event', 'Visualization', 'Click|{0}'.format(d.type), d.id, {
                dimension2: new Date().getTime()
            });
        });
    function reset() {
        d3.transition().duration(750).tween("zoom", function () {
            return function (t) {
                var eventValue;
                scaleFactor = 1;
                translation = [0, 0];
                if (lastScaleFactor > scaleFactor) {
                    eventValue = "Out"
                } else {
                    eventValue = "In"
                }
                lastScaleFactor = scaleFactor
                ga('send', 'event', 'Visualization', 'Zoom', "Reset-" + eventValue, lastScaleFactor, {
                    dimension2: new Date().getTime()
                });
                zoomer.translate(translation).scale(scaleFactor);
                zoom_area.call(zoomer);
                tick();
            };
        });
    }

    document.getElementById("reset-zoom").onclick = reset
}
function activateABrush() {
    var brush_ = d3.svg.brush()
        .x(scaleX)
        .y(scaleY);
    brush_.on("brush", lightUpVizOnBrush(brush_, svg.selectAll('.document')));
    brush_.on("brushend", updateSelected);
    svg.append("g")
        .attr("class", "brush")
        .call(brush_);
}
/*** Set the position of the elements based on data ***/
function tick() {
    rects.attr("x", function (d) {
        return scaleX(d.x);
    })
        .attr("y", function (d) {
            return scaleY(d.y);
        })
    ;
    circles.attr("cx", function (d) {
        return scaleX(d.x);
    })
        .attr("cy", function (d) {
            return scaleY(d.y);
        });
}
function lightUpVizOnBrush(brush, docs) {
    function _brushed() {
        var extent = brush.extent();
        docs.each(function (d) {
            d.selected = false;
        });
        docs.filter(filter_systematic).attr("r", 10);
        docs.filter(filter_primary).attr("width", 12).attr("height", 12);
        search(extent[0][0], extent[0][1], extent[1][0], extent[1][1], docs);
        docs.classed("selected", function (d) {
            return d.selected;
        });

        docs.filter(function(d) {return filter_systematic(d) && d.selected}).attr("r", 15);
        docs.filter(function(d) {return filter_primary(d) && d.selected}).attr("width", 20).attr("height", 20);
    }

    return _brushed
}
function getScale(data, width, height) {
    var x_s = []
    var y_s = []
    for (var i = 0; i < data.length; i++) {
        x_s.push(data[i].x)
        y_s.push(data[i].y)
    }
    var scaleX = d3.scale.linear()
        .domain([Math.min.apply(Math, x_s) - 0.1, Math.max.apply(Math, x_s) + 0.1])
        .range([padding, width - padding]);
    var scaleY = d3.scale.linear()
        .domain([Math.min.apply(Math, y_s) - 0.1, Math.max.apply(Math, y_s) + 0.1])
        .range([height - padding, padding]);
    return [scaleX, scaleY]
}
function updateSelected() {
    var selectedDocs = svg.selectAll(".document").filter(".selected");
    var data = [];
    turnOffViz(svg);
    if (selectedDocs[0].length > 0) {
        selectedDocs.each(function (d) {
            if (d.id != 'current_query') {
                data.push(datum[d.id])
            }
        });
        removeInfoDetails();
        turnOffPanels();
        panelRemoveItems("next-articles", null);
        panelAddItems("next-articles", data);
        // Se muestran en los paneles
        selectedDocs.each(function (d) {
            if (d.id != 'current_query') {
                lightUpPanels(panels, d.id)
            }
        });
    } else {
        removeInfoDetails();
        turnOffPanels();
        panelRemoveItems("next-articles", null);
        panelAddItems("next-articles", document_set)
    }
    ga('send', 'event', 'Visualization', 'Brush', "End", selectedDocs[0].length, {
        dimension2: new Date().getTime()
    });
}
function search(x0, y0, x1, y2, graph) {
    graph.each(function (d) {
        if ((d.x >= x0) && (d.x < x1) && (d.y >= y0) && (d.y < y2)) {
            d.selected = true
        }
    })
}
function lightUpViz(svg, id) {
    var point = svg.select("#" + id);
    if (point) {
        point.classed("active", true)
        point.filter(filter_systematic).attr("r", 15);
        point.filter(filter_primary).attr("width", 20).attr("height", 20);
    }
}
function turnOffViz(svg) {
    var point = svg.selectAll(".active");
    if (point) {
        point.classed("active", false)
        point.filter(filter_systematic).attr("r", 10);
        point.filter(filter_primary).attr("width", 12).attr("height", 12);
    }
}
