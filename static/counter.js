var x;

function setupCounter() {
    return setInterval(function() {
    if (!doing_tour && !saving) {
        seconds_passed -= 1;
        if (seconds_passed == -1) {
            minutes_passed -= 1;
            seconds_passed = 59
        }
        // Display the result in the element with id="demo"

        document.getElementById("counter").innerHTML = getStringTime(minutes_passed) + ":" + getStringTime(seconds_passed);
        // If the count down is finished, write some text
        if (minutes_passed == 0 && seconds_passed == 0) {
            clearInterval(x);
            document.getElementById("counter").innerHTML = "EXPIRED";
            $("#finish-experiment-modal").modal("show")
            startSurvey()
        }
        if (minutes_passed == 15 && seconds_passed == 0){
        enableFinish()
    }
    }
}, 1000);
}

// Update the count down every 1 second
x = setupCounter()

function enableFinish(){
   document.getElementById("finish-experiment").classList.remove("disabled")
        document.getElementById("finish-experiment").disabled = false;
}

function getStringTime(number){
    if (number < 10){
        return "0" + number
    }
    return number
}