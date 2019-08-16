<?php
#ini_set("auto_detect_line_endings", true);
$result = shell_exec("/usr/bin/tail -1000 /tmp/iwconfig.txt 2>&1");
echo "<pre>". $result. "</pre>";
?>
