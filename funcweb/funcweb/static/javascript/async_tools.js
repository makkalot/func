function poll_async_changes(result){
    
    /**
     * Simple method that calls another to check the async results
     */

    //runs on the index page and polls the server side if there is new
    //change in the async db
    //alert(repr(result));
    if (result['changed']==true){
        //alert('Check it ');
        var the_change_msg = "We have some async changes : ";
        the_change_msg = the_change_msg + repr(result['changes'])+" check the <a href='/funcweb/display_async_results'>RESULTS</a> page!";
        getElement('globalerror').innerHTML = the_change_msg;
        window.setTimeout('check_async_change()',50000);
     }
    else
        window.setTimeout('check_async_change()',50000);
}

function check_async_change(){
    /**
     * Method that sends the xmlhttp request to check the changes
     */
    d = loadJSONDoc("/funcweb/check_async?"+queryString(
                {
                'check_change':true
                }
                ));
    d.addCallback(poll_async_changes);
    d.addErrback(poll_error);

}

function poll_error(error){
    var error_msg = "Async Error : probably you have shut down your server or your session has expired try to REFRESH and check your connection !";
    var error_div = getElement("globalerror");
    if (error_div != null){
        error_div.innerHTML = error_msg;
    }
}
