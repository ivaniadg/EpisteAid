/**
 * Created by ivania on 11-04-17.
 */


function removeInfoDetails() {
    metadata.forEach(function (category) {
        removeContentFrom(selected_markup_metadata + category)
    });
    removeContentFrom(selected_markup_metadata + "revisions")
}
function turnOffPanels() {
    var oldSelected = document.querySelectorAll('a.active');
    oldSelected.forEach(function (selected) {
        selected.classList.remove('active');
    })
}
function lightUpPanels(panels, id) {
    var selected = document.querySelectorAll("[data-id='{0}']".format(id));
    selected.forEach(function (item) {
        item.classList.add('active');
        if (item.tagName != "li" && item.tagName != 'LI') {
            user_generated = false
            item.scrollIntoView();
        }
    });
}
function turnOffLastSelected() {
    var list_item = document.querySelector('li.active');
    if (list_item) {
        var elements = document.querySelectorAll("[data-id='{0}'].active".format(list_item.getAttribute("data-id")));
        elements.forEach(function (e) {
            e.classList.remove('active');
        })
    }
}
function lightUpPanel(panel_id, id) {
    var selected;
    if (panel_id == "history-articles") {
        selected = document.querySelectorAll("#history-articles [data-id='{0}']".format(id));
        selected.forEach(function (item) {
            item.classList.add('active');
        });
        if (selected[0]) {
             user_generated = false
            selected[0].scrollIntoView();
        }
    } else {
        selected = document.querySelector("#" + panel_id + "-" + id);
        if (selected) {
            selected.classList.add('active');
             user_generated = false
            selected.scrollIntoView(); // scroll into view
        }
    }
}
function addInfoDetails(doc) {
    metadata.forEach(function (category) {
        var subject = document.getElementById(selected_markup_metadata + category);
        subject.innerHTML = doc[category];
    });
    var div = document.getElementById("selected_article_info");
     user_generated = false
    div.scrollTop = 0;
    div.setAttribute("data-doc-id", doc.id);
    var details = document.getElementById(selected_markup_metadata + "revisions");
    var intro = document.getElementById(selected_markup_metadata + "revisions_intro");
    var button_more = document.getElementById("show-more-revisions");
    if (button_more.children[0].classList.contains("glyphicon-triangle-top")) {
        button_more.children[0].classList.add("glyphicon-triangle-bottom");
        button_more.children[0].classList.remove("glyphicon-triangle-top");
    }
    if (doc['revisions'].length > 0) {
        doc['revisions'].forEach(function (d) {
            var item = document.createElement('li');
            item.setAttribute('id', "revisions" + "-" + d.id);
            if (documentExists(d.id)) {
                var r = datum[d.id].relevance == -1 ? 2 : datum[d.id].relevance;
                item.setAttribute("class", ids2classsification[r]);
                item.onclick = function () {
                    turnOffLastSelected();
                    lightUpPanels([], d.id);
                    lightUpViz(svg, "v-" + d.id);
                    ga('send', 'event', 'Revisions{0}|{1}'.format(doc.relevance, datum[d.id].relevance), 'Click', "{0}|{1}".format(doc.id, d.id),
                        {dimension2: new Date().getTime()});
                }
            }
            item.setAttribute("data-id", d.id);
            var text = document.createTextNode(d.title);
            item.appendChild(text);
            details.appendChild(item)
        });
        details.style.display = "block";
        intro.style.display = 'block';
        if (doc['revisions'].length > 1) {
            button_more.style.display = "block";
            details.classList.toggle('hide-content', true);
            details.classList.toggle('show-content', false);
        } else {
            button_more.style.display = "none";
            details.classList.toggle('hide-content', false);
            details.classList.toggle('show-content', true);
        }
    } else {
        details.style.display = "none";
        intro.style.display = 'none';
        button_more.style.display = "none";
        details.classList.toggle('hide-content', true);
        details.classList.toggle('show-content', false);
    }
}
function documentExists(id) {
    var doc_panel = document.querySelectorAll("[data-id='{0}']".format(id));
    return doc_panel.length > 0
}
function panelItemClick(panel_id, id) {
    turnOffLastSelected();
    var doc = datum[id];
    removeInfoDetails();
    addInfoDetails(doc);
    if (svg && experimentInterface == 'viz') {
        turnOffViz(svg);
        lightUpViz(svg, "v-" + id);
    }
    turnOffPanels()
    lightUpPanel(panel_id, id)
    if (panel_id == "relevant" || panel_id == "non-relevant") {
        lightUpPanel('history-articles', id)
    } else {
        lightUpPanels(['relevant', 'non-relevant'], id)
    }
}
function panelRemoveItems(panel_id, data) {
    if (data) {
        // Elimina este item en particular
        removeItem(panel_id + "_" + data.id)
    }
    else {
        removeContentFrom(panel_id)
    }
}
function panelAddItems(panel_id, data) {
    var placement = "bottom";
    if (panel_id == "next-articles") {
        data = data.filter(function (d) {
            return d.relevance == 0
        })
    } else if (panel_id == "relevant") {
        data = data.filter(function (d) {
            return d.relevance == 1
        })
    } else if (panel_id == "non-relevant") {
        data = data.filter(function (d) {
            return d.relevance == -1
        })
    } else {
        placement = 'top'
    }
    var list = document.getElementById(panel_id);
    var item;
    data.forEach(function (d) {
        item = document.createElement('a');
        item.setAttribute('class', 'list-group-item');
        item.setAttribute('id', panel_id + "-" + d.id);
        item.setAttribute("data-id", d.id);
        var class_ = d.relevance == -1 ? 2 : d.relevance;
        item.classList.add(ids2classsification[class_]);
        item.onclick = function () {
            panelItemClick(panel_id, d.id);
            if (panel_id != "history-articles") {
                ga('send', 'event', 'Panel|{0}'.format(panel_id), 'Click', d.id, {
                    dimension2: new Date().getTime()
                });
            } else {
                ga('send', 'event', 'TimeLine|{0}'.format(d.relevance), 'Click', d.id, {
                    dimension2: new Date().getTime()
                });
            }
        };
        var badge = document.createElement("span");
        badge.setAttribute("class", "badge");
        badge.setAttribute("data-abbr-type", filter_systematic(d) ? "SR" : "PS");
        badge.setAttribute("data-placement", placement);
        badge.setAttribute("data-title", filter_systematic(d) ? "Revision" : "Primary Study");
        badge.setAttribute("data-toggle", "tooltip");
        badge.setAttribute("data-trigger", "hover");
        badge.setAttribute("data-container", 'body');
        var text = document.createTextNode(d.title);
        item.appendChild(badge);
        item.appendChild(text);
        list.appendChild(item);
    });
    if (panel_id == 'history-articles' && item) {
         user_generated = false
        item.scrollIntoView();
    }
}
dragula(
    [document.getElementById("non-relevant"),
        document.getElementById("relevant"),
        document.getElementById("next-articles")],
    {revertOnSpill: false, copy: false})
    .on('drag', function (el, source) {
         var doc_id = el.getAttribute('data-id')
        panelItemClick(source.id, doc_id)
        document_dragged =  el.getAttribute('data-id')
    })
    .on('drop', function (el, target, source) {
        document_dragged =  null
        var doc_id = el.getAttribute('data-id')
        if (source.id != 'next-articles') {
            ga('send', 'event', 'Algorithm', 'Feedback', "{0}|{1}|{2}".format(source.id, target.id, doc_id), {
                dimension2: new Date().getTime()
            });
        }
        el.id = target.id + "-" + doc_id
        var doc = datum[doc_id]
        el.onclick = function () {
            panelItemClick(target.id, doc_id)
            ga('send', 'event', 'Panel', 'Click', "{0}|{1}".format(target.id, doc_id), {
                dimension2: new Date().getTime()
            });
        }
        doc.relevance = classification_ids[target.id] // Aquí ya está el cambio en datum
        changed_documents.push(doc_id)
        svg.select("#v-" + doc_id).style("fill", function (d) {
            return color(d.relevance)
        })
        if (source.id == "next-articles") {
            el.classList.remove("unknown")
        } else if (source.id == "non-relevant") {
            el.classList.remove("non-relevant-article")
        }
        else {
            el.classList.remove("relevant-article")
        }
        if (target.id == "next-articles") {
            el.classList.add("unknown")
        } else if (target.id == "non-relevant") {
            el.classList.add("non-relevant-article")
        }
        else {
            el.classList.add("relevant-article")
        }
        enableSearch();
        updateBadges();
        var action = {
            start: Date.now(),
            id: doc_id,
            relevance: doc.relevance,
            title: doc.title
        }
        actions.push(action)
        addActionTimeLine(action)
        var next_panel = document.getElementById("next-articles");
        if (!next_panel.firstChild) {
            panelAddItems("next-articles", document_set)
            if (brush_on) {
                brush_on = false;
                d3.select(".brush").remove();
            }
            svg.selectAll(".selected").classed("selected", false)
        }
        if (!next_panel.firstChild) {
            // Si todavía no tiene hijos, entonces
            lightUpSearchButton();
        }
    });

var last_scroll = ""

function onScroll(panel_id) {

    return function () {
        if (user_generated && last_scroll != panel_id){
        ga('send', 'event', 'Panel', 'Scroll', panel_id, {
            dimension2: new Date().getTime()
        });
            last_scroll = panel_id
    }else{
            user_generated = true
        }
    }
}
function updateBadges() {
    document.querySelector('#send-feedback span').innerHTML = (changed_documents.length >= minFeedback) ? 0 : minFeedback - changed_documents.length;
    console.log(changed_documents.length)
    console.log(totalFeedback)
    //document.querySelector('#finish-experiment span').innerHTML = ((changed_documents.length + totalFeedback) >= minEnd) ? 0 : minEnd - (changed_documents.length + totalFeedback);
}
function lightUpSearchButton() {
    var button = document.getElementById("send-feedback")
    if (button.classList.contains("btn-default")) {
        button.classList.remove("btn-default")
        button.classList.add("btn-success")
    } else {
        button.classList.remove("btn-success")
        button.classList.add("btn-default")
    }
}

