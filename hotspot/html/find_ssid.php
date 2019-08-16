<?php
$ssid = $_POST["ssid"];

$result = shell_exec("/bin/bash find_ssid.sh $ssid $pwd");

$split = explode("\n", $result);
array_pop($split);

foreach ($split as $tmp)
    echo "<option value=\"$tmp\">$tmp</option>"

#echo "$result"

?>
