function addDomAjaxREsult(){
    
    //just creates the sturctore that is in result.html
    if (getElement('resultbox')==null){
    var result_header = DIV({'align':'center','class':'graytexts'});
    result_header.innerHTML = "Result";
    var minions = DIV({'class':'minions','id':'minions'},result_header);
    var results = DIV({'class':'resultbox','id':'resultbox'});
    var main = DIV(
            {'class':'resultbigbox','id':'resultbigbox'},
            minions,
            results
            );

    //adding those to main part ..
    var result_container=getElement("resultcontent");
    appendChildNodes(result_container,main);
    }
    else
        getElement('resultbox').innerHTML = "";
}


function remoteFormRequest(form, target, options) {
	var query = Array();
    var contents = formContents(form);
    for (var j=0; j<contents[0].length; j++){
        if(compare(target,'group_small')==0){
            if(!query[contents[0][j]]){
                query[contents[0][j]] = [];
            }
            //add that here
            query[contents[0][j]].push(contents[1][j]);

        }
        else
            query[contents[0][j]] = contents[1][j];
    }
	query["tg_random"] = new Date().getTime();
	//makePOSTRequest(form.action, target, queryString(query));
	remoteRequest(form, form.action, target, query, options);
	return true;
}

function remoteRequest(source, target_url, target_dom, data, options) {
    //before
    if (options['before']) {
        eval(options['before']);
    }
    if ((!options['confirm']) || confirm(options['confirm'])) {
        makePOSTRequest(source, target_url, getElement(target_dom), queryString(data), options);
        //after
        if (options['after']) {
            eval(options['after']);
        }
    }
	return true;
}

function makePOSTRequest(source, url, target, parameters, options) {
  var http_request = false;
  if (window.XMLHttpRequest) { // Mozilla, Safari,...
     http_request = new XMLHttpRequest();
     if (http_request.overrideMimeType) {
        http_request.overrideMimeType('text/xml');
     }
  } else if (window.ActiveXObject) { // IE
     try {
        http_request = new ActiveXObject("Msxml2.XMLHTTP");
     } catch (e) {
        try {
           http_request = new ActiveXObject("Microsoft.XMLHTTP");
        } catch (e) {}
     }
  }
  if (!http_request) {
     alert('Cannot create XMLHTTP instance');
     return false;
  }

    var insertContents = function () {
        if (http_request.readyState == 4) {
            // loaded
            if (options['loaded']) {
                eval(options['loaded']);
            }
            if (http_request.status == 200) {
                if(target) {
                    var is_error = true;
                    //some hacky olution to catch the python errors
                    try{
                        var check_error = evalJSON(http_request.responseText);
                                    }
                        catch(e){
                            //There is no error in request
                            is_error = false;
                        }
                        if (is_error == true){
                            if (compare(check_error['fg_flash'],null)!=0)
                                connection_error(check_error['tg_flash']);
                            else
                                is_error = false;
                        }
                        
                        if (is_error == false)
                            target.innerHTML = http_request.responseText;
                }
                //success
                if (options['on_success']) {
                    eval(options['on_success']);
                }
            } else {
                //failure
                if (options['on_failure']) {
                    eval(options['on_failure']);
                //it seems to be an expiration ...
                } else if(http_request.status == 403){
                    alert('It seems that current session expired you should log in !');
                    window.location = window.location.href;
                }
                else {
                    alert('There was a problem with the request. Status('+http_request.status+')');
                }

            }
            //complete
            if (options['on_complete']) {
                eval(options['on_complete']);
            }
        }
    }
  
    http_request.onreadystatechange = insertContents;
    http_request.open('POST', url, true);
    http_request.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    http_request.setRequestHeader("Content-length", parameters.length);
    http_request.setRequestHeader("Connection", "close");
    http_request.send(parameters);
}

function glob_submit(form_element,target_dom){
    /*
     * Because it is a common function we have to move it here for better results
     * form_element is what we submit and the target_dom is the place that will be replaced
     */
    
    before_action = null;
    //sometimes we are not sure which dom to get so is that situation
    if(compare(target_dom,'not_sure')==0)
        target_dom = which_dom();

    //if we are in the index page should to that 
    if (compare(target_dom,'minioncontent')==0){
        before_action = "hideElement(getElement('resultcontent'));hideElement(getElement('widgetcontent'));hideElement(getElement('methotdscontent'));hideElement(getElement('modulescontent'));";
    }
    else if(compare(target_dom,'groupscontent')==0){
        before_action = "hideElement(getElement('miniongroupcontents'));";
    }
    
    form_result = remoteFormRequest(form_element,target_dom, {
            'loading': null,
            'confirm': null, 
            'after':null,
            'on_complete':null, 
            'loaded':null, 
            'on_failure':null, 
            'on_success':null, 
            'before':before_action 
            }
            );
    
    return form_result;
}

function which_dom(){
    /*
     * We use the glob submit in lots of places so we should
     * know where we are actually so that method will handle that
     */

    //that is for index.html
    dom_result = getElement('minioncontent');
    if (dom_result != null){
        //alert("Im giving back the minioncontent");
        return 'minioncontent';

    }
    
    //it is for groups_main.html
    dom_result = getElement('minion_small');
    //will change it later
     if (dom_result != null){
        return 'minion_small';
    }

    return dom_result;
}
