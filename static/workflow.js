/**
 * Created by ivania on 13-04-17.
 */

var num_loads = 0

function getUser() {
    var user_id = document.getElementById("user-id").value
    var xhttp = new XMLHttpRequest();   // new HttpRequest instance
    xhttp.open("POST", "/get_user");
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhttp.send(JSON.stringify({
        user_id: user_id
    }));

    xhttp.onreadystatechange = function () {
            if (xhttp.readyState == 4 && xhttp.status == 200) {
                var data = JSON.parse(xhttp.responseText)
                var link = data["link"]
                var survey = data["survey"]
                ga('set', 'dimension1', user_id);
                    //document.getElementById("footer-m").style.display = none;
                removeItem("footer-m")
                console.log(USE_SURVEY)
                if (USE_SURVEY && survey == false){
                    startSurvey(link, user_id)
                }
                else{
                    $(".carousel").carousel(2)
                }
            }
            else if (xhttp.readyState == 4 && xhttp.status == 404) {
                document.getElementById("user-form").classList.add("has-error")
                alert("No se encontró \"" + document.getElementById("user-id").value + "\". Verifique que este código sea el correcto." +
                      "Si sigue con problemas envíe un email a episteaid@gmail.com con el asunto [\"URGENTE\"]")
            }else{
                console.log('Problema en server')
            }
        };

}

function startSurvey(link, user_id) {

    iframe = document.getElementById("survey");
    iframe.onload = function() {
        if (num_loads == 0){
            num_loads += 1;
        }else{
            checkSurveyResponse(iframe, link, user_id);
        }
    };
    iframe.src = link
    $(".carousel").carousel(1)
}

function checkSurveyResponse(iframe, link, user_id) {
    var xhttp = new XMLHttpRequest();   // new HttpRequest instance
    xhttp.open("GET", "/survey/{0}/{1}".format(user_id, "init"));
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhttp.send();
    xhttp.onreadystatechange = function () {
        if(xhttp.readyState==4 && xhttp.status==200) {
            data = JSON.parse(xhttp.responseText)
            if (data["found_survey"]){
                $(".carousel").carousel(2)
            }
            else{
                iframe.src = link;
                alert("No hemos recibido tu respuesta del cuestionario. Por favor respondenlo.");
                num_loads = 0;
            }
        }
    }
}


function startSession() {
    document.getElementById('user-form').submit();
    document.getElementById("start-button").classList.add("disabled")
}

