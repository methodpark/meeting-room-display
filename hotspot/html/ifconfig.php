<?php
#ini_set("auto_detect_line_endings", true);
$result = shell_exec("/usr/bin/tail -1000 /tmp/ifconfig.txt");
echo "<pre>". $result. "</pre>";
?>
