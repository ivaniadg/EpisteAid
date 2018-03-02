/**
 * Created by ivania on 06-05-16.
 */

if(typeof(String.prototype.trim) === "undefined")
{
    String.prototype.trim = function()
    {
        return String(this).replace(/^\s+|\s+$/g, '');
    };
}
function removeItem(id) {
    var elem = document.getElementById(id);
    elem.parentNode.removeChild(elem);
}

function removeContentFrom(box) {
    var myNode = document.getElementById(box);
    while (myNode.firstChild) {
        myNode.removeChild(myNode.firstChild);
    }
}
if (!String.prototype.format) {
  String.prototype.format = function() {
    var args = arguments;
    return this.replace(/{(\d+)}/g, function(match, number) {
      return typeof args[number] != 'undefined'
        ? args[number]
        : match
      ;
    });
  };
}

function getValues(dictionary){
    var values = Object.keys(dictionary).map(function(key){
            return dictionary[key];
        });
    return values
}