<?php
$ssid = $_POST["ssid"];

$result = shell_exec("/bin/bash rem_ssid.sh \"$ssid\"");

header("Location: index.php?ssid=$ssid&rem=$result");
exit();
?>
