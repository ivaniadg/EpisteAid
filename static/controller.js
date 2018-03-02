/**
 * Created by ivania on 28-03-17.
 */

function enableSearch() {
    // Habilitar bottón
    if (changed_documents.length >= minFeedback || document.getElementById("next-articles").children.length == 0) {
        var button = document.getElementById("send-feedback")
        button.classList.remove('disabled')
        button.disabled = false;
    }
}

function disableSearch() {
    var button = document.getElementById("send-feedback")
    button.classList.add('disabled')
    button.disabled = true;
    if (button.classList.contains("btn-success")) {
        button.classList.remove("btn-success")
        button.classList.add("btn-default")
    }

}

function showLoaderGif(id){
    var loader = document.getElementById(id)
        loader.style.display = "inline"
}

function removeLoaderGif(id){
    var loader = document.getElementById(id)
        loader.style.display = "none"
}

function searchMore() {
    // Obtener clases de docs que cambiaron
    if (changed_documents.length >= minFeedback) {

        var unknownDocs = getValues(datum).filter(function (d) {
            return d.relevance == 0
        });
        showLoaderGif('loading-search')
        var eventLabel = (unknownDocs.length > 0) ? "True" : "False"
        ga('send', 'event', 'Algorithm', 'Search', eventLabel, unknownDocs.length, {
            dimension2: new Date().getTime()
        });
        var feedback = []
        changed_documents.forEach(function (d) {
            feedback.push(datum[d].relevance)
        });

        // Envíamos feedback
        var xhttp = new XMLHttpRequest();   // new HttpRequest instance
        xhttp.open("POST", "/send_feedback/{0}/{1}/{2}".format(user_id, minutes_passed, seconds_passed));
        xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
        xhttp.send(JSON.stringify({
            documents: changed_documents,
            feedback: feedback,
            user_id: user_id,
            actions: actions
        }));

        totalFeedback = totalFeedback + changed_documents.length;
        changed_documents = [];
        actions = [];
        xhttp.onreadystatechange = function () {
            if (xhttp.readyState == 4 && xhttp.status == 200) {
                removeContentFrom("vis-svg")
                removeContentFrom("next-articles")
                var data = JSON.parse(xhttp.responseText);
                document_set = data["documents"];
                // Aquí solo se agregan documentos. Los que no están se eliminan
                unknownDocs.forEach(function (d) {
                    if (changed_documents.indexOf(d.id) == -1 && d.id != document_dragged){
                        delete datum[d.id]
                    }
                });
                document_set = document_set.filter(function(d){return changed_documents.length > 0? changed_documents.indexOf(d.id) == -1: true});
                document_set = document_set.filter(function(d){return d.id != document_dragged? true : false});

                document_set.forEach(function (e) {
                    datum[e.id] = e
                });

                panelAddItems("next-articles", document_set)
                $('[data-toggle="tooltip"]').tooltip()
                var documents = getValues(datum)
                if (experimentInterface == 'viz') {
                    loadVisDocs(documents, "vis", filter_primary, filter_systematic)
                }

                disableSearch();
                updateBadges();
                removeLoaderGif('loading-search');

            }
            else {
                console.log('Waiting')
            }
        };
    }
}
function startExperiment() {
    showLoaderGif('loading-finish-experiment-modal')
    removeContentFrom("next-articles")
    removeContentFrom("relevant")
    removeContentFrom("non-relevant")
    removeContentFrom("vis")
    removeContentFrom("history-articles")
    removeInfoDetails();
    var div = document.getElementById("selected_article_info");
    div.setAttribute("data-doc-id", "");
    num_loads = 0
    action_id = 0
    actions = []
    changed_documents = []
    start_time = new Date().getTime()
    totalFeedback = 0;
    minutes_passed = 30
    seconds_passed = 0
    // Cargar info
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", "/start_experiment/" + user_id);
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhttp.send();
    xhttp.onreadystatechange = function () {
        if (xhttp.readyState == 4 && xhttp.status == 200) {
            var data = JSON.parse(xhttp.responseText)
            document.getElementById("document-title").innerHTML = data["document_set_title"]
            document_set_title = data["document_set_title"]
            model = data['model']
            document_set_id = data["document_set_id"];
            experimentInterface = data['interface'];
            ga('send', 'event', 'Experiment', 'StartExperiment', document_set_id, {
                dimension2: new Date().getTime()
            });
            ga('set', 'dimension3', model);
            ga('set', 'dimension4', document_set_id);
            ga('set', 'dimension5', experimentInterface);
            svg = d3.select("#vis")
                        .append("svg")
                        .attr("id", "vis-svg")

            document_set = data["documents"]
            datum = {}
            document_set.forEach(function (e) {
                datum[e.id] = e
            })

            panelAddItems("next-articles", document_set)
            panelAddItems("relevant", document_set)
            if (experimentInterface == 'noviz') {
                removeVizForExperiment();
            } else {
                addVizForExperiment();
                loadVisDocs(document_set, "vis", filter_primary, filter_systematic);
                changeMethod(); // Por que si no la viz aparece rara
                var transform_selector = document.getElementById("transform_selector");
                transform_selector.selectedIndex = 0;
            }
            transformTimeLineData(actions)
            disableSearch()
            updateBadges();
            document.getElementById("finish-experiment").classList.add("disabled")
            document.getElementById("finish-experiment").disabled = true;

            $("#finish-experiment-modal").carousel(0).modal('hide');

            startFeatureTour();
            setupCounter()
            removeLoaderGif('loading-finish-experiment-modal')



        }
    }
}
function finishExperiment() {
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", "/finish_experiment/{0}/{1}/{2}".format(user_id, minutes_passed, seconds_passed));
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhttp.send();
    ga('send', 'event', 'Experiment', 'FinishExperiment', document_set_id, {
        dimension2: new Date().getTime()
    });

}
function sendFeedback(endSession, modal_id, next_panel) {
    var xhttp = new XMLHttpRequest();
    if (changed_documents.length > 0) {
        var feedback = [];
        changed_documents.forEach(function (d) {
            feedback.push(datum[d].relevance)
        });
        totalFeedback = totalFeedback + changed_documents.length;
        xhttp.open("POST", "/send_feedback/{0}/{1}/{2}".format(user_id, minutes_passed, seconds_passed));
        xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
        xhttp.send(JSON.stringify({
            documents: changed_documents,
            feedback: feedback,
            actions: actions,
            user_id: user_id,
            end: endSession
        }));
        if (endSession) {
            xhttp.onreadystatechange = function () {
                    if (xhttp.readyState == 4 && xhttp.status == 200) {
                        $("#" + modal_id).carousel(next_panel)
                        removeLoaderGif("loading-"+modal_id)
                    }
                }

        }
        changed_documents = [];
        actions = []

    }
}
function endSession(send_changes, next_panel, modal_id) {
    if (sessionOn) {
        showLoaderGif("loading-" + modal_id)
        if (changed_documents.length > 0 && send_changes) {
            sendFeedback(true, modal_id, next_panel);
            ga('send', 'event', 'Experiment', 'EndSession', 'SaveChanges', changed_documents.length, {
                dimension2: new Date().getTime()
            });
        } else {

            ga('send', 'event', 'Experiment', 'EndSession', 'DontSaveChanges', changed_documents.length, {
                dimension2: new Date().getTime()
            });
            sendEndSession(user_id, modal_id, next_panel)
        }


        sessionOn = false
    }
}
function sendEndSession(user_id, modal_id, next_panel) {
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", "/finish_session/{0}/{1}/{2}".format(user_id, minutes_passed, seconds_passed));
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhttp.send();

    xhttp.onreadystatechange = function () {
        if (xhttp.readyState == 4 && xhttp.status == 200) {
            $("#" + modal_id).carousel(next_panel)
            removeLoaderGif("loading-"+modal_id)
        }
    }
}
function startSurvey() {
    if (minutes_passed < 15) {
        clearInterval(x);
        showLoaderGif('loading-finish-experiment-modal')
        finishExperiment()
        sendFeedback(false, null, null);
        var xhttp = new XMLHttpRequest();
        xhttp.open("GET", "/get_experiment_survey/" + user_id);
        xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
        xhttp.send();
        xhttp.onreadystatechange = function () {
            if (xhttp.readyState == 4 && xhttp.status == 200) {
                var data = JSON.parse(xhttp.responseText)
                if (!USE_SURVEY){
                    if (data['experiments_left'] > 0) {
                        $("#finish-experiment-modal").carousel(2); // Preguntar si quiere seguir
                    } else {
                        endSession(false, 3, "finish-experiment-modal"); // Cerrar y decir quue terminó
                        ga('send', 'event', 'Experiment', 'FinishExperiment', document_set_id, {
                            dimension2: new Date().getTime()
                        });
                        ga('send', 'event', 'Experiment', 'FinishExperiment', "endAll", {
                            dimension2: new Date().getTime()
                        });
                    }
                }
                var link = data["link"]
                var iframe = document.getElementById("survey")
                iframe.onload = function () {
                     removeLoaderGif('loading-finish-experiment-modal')
                    if (num_loads == 0) {

                        removeLoaderGif("loading-survey")

                        num_loads += 1;
                    } else {
                        num_loads = 0;

                        showLoaderGif("loading-survey")
                        checkSurveyResponse(iframe, link, data['experiments_left'])
                    }
                };
                iframe.src = link;
            }
            else {
                console.log('Esperando link encuesta')
            }
        };


        ga('send', 'event', 'Experiment', 'StartSurvey', document_set_title, {
            dimension2: new Date().getTime()
        });
        $("#finish-experiment-modal").carousel(1)
    }
}
function toggleHelp(button) {
    var element = document.getElementById("history-articles")
    if (!showingHints) {
        showingHints = true
        element.style.opacity = 1;
        element.style.visibility = 'visible';
        button.innerHTML = "Cerrar Ayuda"

        intro.showHints();
        if (experimentInterface == 'noviz'){
            intro.hideHint(6);
            intro.hideHint(7);
            intro.hideHint(8);
            intro.hideHint(9);
    }
         ga('send', 'event', 'Help', 'Hints', "Show", {
        dimension2: new Date().getTime()
    });
    } else {
        showingHints = false
        element.style.opacity = 0;
        element.style.visibility = 'hidden';
        button.innerHTML = "Ver Ayuda"
        intro.hideHints();
        ga('send', 'event', 'Help', 'Hints', "Hide", {
        dimension2: new Date().getTime()
    });
    }

}
function startFeatureTour() {
    intro = introJs();
    intro.setOptions({
        nextLabel: "siguiente",
        prevLabel: "anterior",
        skipLabel: "saltar",
        doneLabel: "comenzar",
        hidePrev: true,
        hideNext: true,
        exitOnEsc: true,
        exitOnOverlayClick: false,
        keyboardNavigation: true,
        showStepNumbers: false,
        showButtons: true,
        showProgress: true,
        overlayOpacity: 0.8,
        disableInteraction: true,
        hintButtonLabel: 'OK'
    });
    intro.onchange(function (targetElement) {
        var id = targetElement.id
        if (id == 'see-timeline') {
            var element = document.getElementById("history-articles")
            element.style.opacity = 1;
            element.style.visibility = 'visible';
        } else if (id == 'counter') {
            var element = document.getElementById("history-articles")
            element.style.opacity = 0;
            element.style.visibility = 'hidden';
        } else if (experimentInterface == "noviz") {
            if (id == 'viz') {
                intro.nextStep();
            } else if (id == 'transform_selector') {
                intro.nextStep();
            }
        }
    });

    intro.onexit(function() {
        doing_tour = false;
        ga('send', 'event', 'Help', "Tour","End", {
        dimension2: new Date().getTime()
    });
});
    ga('send', 'event', 'Help', "Tour","Start", {
        dimension2: new Date().getTime()
    });
    doing_tour = true;

    intro.start();


}
function checkSurveyResponse(iframe, link, experiments_left) {
    var xhttp = new XMLHttpRequest();   // new HttpRequest instance
    xhttp.open("GET", "/survey/{0}/{1}-{2}-{3}".format(user_id, model, experimentInterface, document_set_id));
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhttp.send();
    xhttp.onreadystatechange = function () {
        if (xhttp.readyState == 4 && xhttp.status == 200) {
            data = JSON.parse(xhttp.responseText)
            if (data["found_survey"]) {
                if (experiments_left > 0) {
                    $("#finish-experiment-modal").carousel(2); // Preguntar si quiere seguir
                } else {
                    endSession(false, 3, "finish-experiment-modal"); // Cerrar y decir quue terminó
                    ga('send', 'event', 'Experiment', 'FinishExperiment', document_set_id, {
                        dimension2: new Date().getTime()
                    });
                    ga('send', 'event', 'Experiment', 'FinishExperiment', "endAll", {
                        dimension2: new Date().getTime()
                    });
                }
                num_loads = 0;
            }
            else {
                iframe.src = link;
                alert("No hemos recibido tu respuesta del cuestionario. Por favor respondenlo.");
                num_loads = 0;
            }
        }
    }
}
function removeVizForExperiment() {
    // sacar viz
    document.getElementById("vis").style.display = 'none';
    document.getElementById("transform_selector").style.display = 'none';
    document.getElementById("reset-zoom").style.display = 'none';
    document.getElementById("change-mode").style.display = 'none';
    document.getElementById('selected_article_info').style.maxHeight = '73vh';
}
function addVizForExperiment() {
    document.getElementById("vis").style.display = 'block';
    document.getElementById("vis").style.height = '45vh';
    document.getElementById("reset-zoom").style.display = 'inline';
    document.getElementById("change-mode").style.display = 'inline';
    document.getElementById("transform_selector").style.display = 'inline';
    document.getElementById('selected_article_info').style.maxHeight = '30vh';
}

function showMoreRevisions(button_id) {
    var span = document.querySelector("#{0} span".format(button_id));
    var revisions = document.getElementById("selected_article_revisions");
    if (span.classList.contains("glyphicon-triangle-bottom")) {
        span.classList.add("glyphicon-triangle-top");
        span.classList.remove("glyphicon-triangle-bottom");
        revisions.classList.remove('hide-content');
        revisions.classList.add("show-content");
    } else {
        span.classList.add("glyphicon-triangle-bottom");
        span.classList.remove("glyphicon-triangle-top");
        revisions.classList.remove("show-content");
        revisions.classList.add('hide-content')
    }
}

function onScrollDetails() {
    if (user_generated) {
        var div = document.getElementById("selected_article_info");
        var doc = div.getAttribute("data-doc-id")
        if (last_scroll != doc) {
            ga('send', 'event', 'Details', 'Scroll', doc, {
                dimension2: new Date().getTime()
            });
            last_scroll = doc
        }
    }else{
        user_generated = true
    }
}
