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
