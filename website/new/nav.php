<?php


  switch ($current_page) {

	case "about":
		echo "<ul id=\"nav\">
  		 <li id=\"active\"><a href=\"index.php\">About</a></li>
  		 <li><a href=\"https://fedorahosted.org/projects/func\">Wiki</a></li>
 		</ul>";
		break;
	default:
		echo " <ul id=\"nav\">
  		 <li id=\"active\"><a href=\"index.php\">About</a></li>
  		 <li><a href=\"http://hosted.fedoraproject.org/projects/func/\">Wiki</a></li>
 		</ul>";
		break;

}

?>

