/**
 * Created by ivania on 10-04-17.
 */

function transformTimeLineData(history_data){
    var data_formatted = [];
    history_data.forEach(function (action){
        if (datum[action.id])
    {
        data_formatted.push({start: action.start, title: datum[action.id]['title'], id: action.id, relevance: action.relevance})
    }
    });
    actions = [];
     panelAddItems('history-articles', data_formatted)


}

function addActionTimeLine(action){
    panelAddItems('history-articles', [action])
}


function seeTimeLine(button_id){
    var eventLabel;
    var element = document.getElementById("history-articles");
    var span = document.querySelector("#{0} span".format(button_id));

    if (span.classList.contains("glyphicon-triangle-top")) {
        element.style.opacity = 1;
        element.style.visibility = 'visible';
        span.classList.add("glyphicon-triangle-bottom");
        span.classList.remove("glyphicon-triangle-top");
        eventLabel = "Open";
    }
    else{
        span.classList.add("glyphicon-triangle-top");
        span.classList.remove("glyphicon-triangle-bottom");
        eventLabel = "Close";
        element.style.opacity = 0;
        element.style.visibility = 'hidden';
    }
    ga('send', 'event', 'Timeline', 'Visibility', eventLabel, document.getElementById('history-articles').children.length  , {
                    dimension2: new Date().getTime()
                });

}





