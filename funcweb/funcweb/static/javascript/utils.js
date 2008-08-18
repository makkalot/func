function check_all(class_name){
    var check_boxes = getElementsByTagAndClassName('input',class_name);
    for (var check_element in check_boxes){
        if (compare(check_boxes[check_element].checked,false)==0){
            check_boxes[check_element].checked = true;
        }
    }
}

function uncheck_all(class_name){
    var check_boxes = getElementsByTagAndClassName('input',class_name);
    for (var check_element in check_boxes){
        if (compare(check_boxes[check_element].checked,true)==0)
            check_boxes[check_element].checked = false;
    }
   
}

function checkController(class_name,check_element){
    if (check_element.checked == true){
        check_all(class_name);
    }
    else
        uncheck_all(class_name);
}

/*
 * Some ajaxian methods here (minion related stuff mostly !)
 * These methods will replace the jquery and will let the Mochikit
 * do all the stuff here !
 */

//------------------------------------------------------------------------------

function list_minion_modules(minion_name){
    /*
     * Method that hanles all the stuff on index.html
     * Therefore when you change something on index.html you should change
     * that method also if it affects the related div ids below 
     */

    //firstly do some hidings here 
    hideElement(getElement('resultcontent'));
    hideElement(getElement('widgetcontent'));
    hideElement(getElement('methotdscontent'));
    hideElement(getElement('modulescontent'));
    var base_url = '/funcweb/minion';
    var data_pack = {'name':minion_name};
    var div_to_replace = 'modulescontent';
    //send the JSON request !
    send_some_JSON(base_url,data_pack,div_to_replace);
}

function list_module_methods(minion_name,module_name){
    
    //listing methods for specified module works for modules.html

    hideElement(getElement('widgetcontent'));
    hideElement(getElement('resultcontent'));
    hideElement(getElement('methotdscontent'));
    var base_url = '/funcweb/minion';
    var data_pack = {
        'name':minion_name,
        'module':module_name
    };
    var div_to_replace = 'methotdscontent';
    send_some_JSON(base_url,data_pack,div_to_replace);

}

function get_method_widget(minion_name,module_name,method_name){

    // The method widget generator part works for methods.html 

    hideElement(getElement('resultcontent'));
    hideElement(getElement('widgetcontent'));
    var base_url = '/funcweb/method_display';
    var data_pack = {
        'minion':minion_name,
        'module':module_name,
        'method':method_name
    };
    var div_to_replace = 'widgetcontent';
    send_some_JSON(base_url,data_pack,div_to_replace);
}


function get_hosts_by_group(group_name){
    
    //it is a part from group management api
    //gets the hosts for specified group_name
    hideElement(getElement('resultcontent'));
    var base_url = '/funcweb/list_host_by_group';
    var data_pack = {
        'group_name':group_name
    };
    var div_to_replace = 'miniongroupcontents';
    send_some_JSON(base_url,data_pack,div_to_replace);
}

function execute_link_method(minion,module,method){

    //execution part for methods that accept no arguments
    hideElement(getElement('resultcontent'));
    var base_url = '/funcweb/execute_link';
    var data_pack = {
        'minion':minion,
        'module':module,
        'method':method
    };
    var div_to_replace = 'resultcontent';
    send_some_JSON(base_url,data_pack,div_to_replace);
}

function send_some_JSON(base_url,data_pack,div_to_replace){
    /*
     * A common method that will responsible for sending 
     * simple Http request to server !
     */
    var d = doSimpleXMLHttpRequest(base_url, data_pack);
    //var d = loadJSONDoc(base_url+queryString(data_pack));
    d.addCallback(replace_div_success,div_to_replace);
    //The errback will be a common method here !
    d.addErrback(connection_error);

}

function replace_div_success(div_to_replace,result){
    /*
     * The common callback for ajax requests
     */

    var server_text = result.responseText;
    var is_error = true;
    var check_error = null;
    
    //Because we got a response text it may not be a json object we should control it
    //we report the errors with tubogears tg_flash variable so the control below
    //simply tries to convert the response into JSON doc and pull the tg_flash variable's
    //value. If it is null it seems tobe a normal response !
    try{
        check_error = evalJSON(server_text);
    }
    catch(e){
        //There is no error in request
        is_error = false;
    }

    if (is_error == true){
        //js is so stupid damn :|
        if (compare(check_error['fg_flash'],'null')!=0)
            connection_error(check_error['tg_flash']);
        else{
            alert("It was marked as non error");
            is_error = false;
        }
    }

    if (is_error == false){
        //Put the result into the target div
        var replace_div = getElement(div_to_replace);
        if (replace_div != null){
            //first make it to appear here
            showElement(replace_div);
            replace_div.innerHTML = server_text;
        }
    }
}

function connection_error(error){
    // The common errback method
    var error_msg = "Async Request Error : You may try checking your connection and refresh your page! :" + repr(error);
    alert("We got error in Async Request check the more detailed error report at the TOP of the page !");    
    var error_div = getElement("globalerror");
            if (error_div != null){
                error_div.innerHTML = error_msg;
            }
}

//-------------------------------------------------------------------------------------------------------------
function check_async_result(job_id){
    //sends some request to get the current job ids status :)
    hideElement(getElement('resultcontent'));
    var base_url = '/funcweb/check_job_status';
    var data_pack = {
        'job_id':job_id
    };
    var div_to_replace = 'resultcontent';
    send_JSON_DOC_info(base_url,data_pack,div_to_replace);

}


function send_JSON_DOC_info(base_url,data_pack,div_to_replace){
    /*
     * That method is for getting the result that comes
     * from minion side parsed in JSON format
     * maybe used for other things also ...
     */

    d=loadJSONDoc(base_url,data_pack);
    d.addCallback(load_parsed_result_tree,div_to_replace);
    d.addErrback(connection_error);
    
}

function load_parsed_result_tree(div_to_replace,result){
    /*
     * The callback for showing the tree structure
     */

    //check for errors
    if (compare(result['fg_flash'],null)!=0){
        connection_error(result['tg_flash']);
        return;
    }
    
    //firstly load the div that will include the tree
    var replace_div = getElement(div_to_replace);
    if (replace_div != null){
        //first make it to appear here
        showElement(replace_div);

        //place here the tree div that will show up the tree structure
        var html_code = '<div class="resultbigbox" id="resultbigbox"><div align="center" class="graytexts">Result</div><div class="resultbox" id="resultbox"><div id="treeboxbox_tree" style="width:200;height:200;border:0"></div></div></div>'
        replace_div.innerHTML = html_code;
        }

    //now load the tree
    tree=new dhtmlXTreeObject("treeboxbox_tree","100%","100%",0);
    tree.setImagePath("/funcweb/static/images/imgs/");
    tree.loadJSONObject(result['minion_result']);
    alert("The tree should be loaded");


}


