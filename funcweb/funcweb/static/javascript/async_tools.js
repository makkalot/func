function poll_async_changes(result){
    
    /**
     * Simple method that calls another to check the async results
     */

    //runs on the index page and polls the server side if there is new
    //change in the async db 
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

}

function poll_error(error){
    alert("Some error in xmlHttpRequest check your connection : ");
}
