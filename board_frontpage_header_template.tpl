<!DOCTYPE html>
<html lang="en">
<head>
<!-- Meta data for search engines ... Not important. -->
<meta name="description" content="Blackboard for distributed systems course">
<meta name="keywords" content="Lab">
<meta name="author" content="Beshr Al Nahas">
<!-- Important for the browser to show the page in the correct encoding -->
<meta charset="UTF-8">
<!-- Important for the browser to include the jQuery library. It is used to update the page contents automatically. -->
<script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.4/jquery.min.js"></script>
<!-- Inlined javascript code. This could be optionally hosted in another file on the server and included using 'src' attribute as above -->
<script>

var page_reload_timeout = 5; //in seconds
var page_reload_count = 0;

function update_contents(){
    page_reload_count += 1;
    $("#boardcontents_placeholder").load("/board #boardcontents_placeholder", function (data, status) {
        //alert("Data: " + data + "\nStatus: " + status);
        $("#boardcontents_status_placeholder").text(page_reload_count + ": " + status);
    });
}

function reload_countdown(remaining) {
    $("#countdown_placeholder").text("reloading page in: " + remaining + " seconds.");
    if (remaining <= 0) {
        remaining = page_reload_timeout;
        update_contents();
    }

    setTimeout(function () {
        reload_countdown(remaining - 1);
    }, 1000);
}

$(document).ready(function () {
    reload_countdown(page_reload_timeout);

    $(".entryform").submit(update_contents);
});
</script>
<!-- this place defines the style (format) for different elements of the page -->
<style>
.status {
    color: red;
    font-size: 75%; 
}

.entry_title {
    margin: 2px 0px 0px 0px;      
    color: blue;
    font-size: 110%;
    font-weight: bold;
}

.entryform {
    margin: 2px 0px 0px 0px;      
    color: blue;
}

#clock_placeholder {
    font-size: 75%;
}

#countdown_placeholder {
    font-size: 75%;
}

#boardcontents_status_placeholder {
    font-size: 75%; color: gray;
}

footer {
    margin: 10px 0px 0px 0px;
    font-size: 75%; 
    color: gray;
}

#boardcontents_placeholder {
    margin: 10px 0px 0px 0px;      
    border: 1px dotted green;
}

#boardtitle_placeholder {
    font-size: 125%;
    font-weight: bold; 
}
</style>
    <title>Distributed board - TDA596 (Chalmers)</title>
</head>
<body>
    <!-- this place will show a count down for the automatic reload of the board contents, downloaded periodically from the server using the javascript function reload_countdown. -->
    <div id="countdown_placeholder"></div>
    <!-- this place will show the actual contents of the blackboard. 
    It will be reloaded automatically from the server -->
    <!-- This place shows the status of the auto-reload. 
    An error shown here means the server is not responding -->
    <div id="boardcontents_status_placeholder">0: success</div>

    <!-- This is a target for forms to prevent reloading the page on form submit. We handle the update in the script instead. USE style="display:none" to hide it -->   
    <iframe name="noreload-form-target" width="90%" height="50" src="about:blank" frameborder="0" scrolling="yes" resizable seamless></iframe>

    <!-- This place shows the text box used to enter data to the blackboard by posting a request to the server -->
    <div id="board_form_placeholder">
        <h3>Submit to board</h3>
        <form id="usrform" target="noreload-form-target">
            <input type="text" name="entry" size="100%" autofocus required />
            <input type="submit" formmethod="post" formaction="board" value="Submit to board"/>
        </form>
    </div>

    <!-- The board contents come here -->  
