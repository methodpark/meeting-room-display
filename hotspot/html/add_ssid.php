<?php
$ssid = $_POST["ssid"];
$pwd = $_POST["pwd"];

if (strlen($ssid) == 0) {
    #ssid not set
    $add = "not_set";
} else if (strlen($pwd) < 8) {
    #password too short - break
    $add = "too_short";
} else {
    exec("/bin/bash add_ssid.sh \"$ssid\" \"$pwd\"");
    $add = "success";
}

header("Location: index.php?ssid=$ssid&add=$add");
exit();
?>
