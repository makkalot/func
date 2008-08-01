function checkAll(form_element){

}

function uncheckAll(form_element){
    
}

function checkController(form_element,check_element){
    if (check_element.checked == 1){
        checkAll(form_element);
    }
    else
        uncheckAll(form_element);
}
