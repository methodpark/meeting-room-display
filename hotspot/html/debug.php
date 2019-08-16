<?php
#ini_set("auto_detect_line_endings", true);
$result = shell_exec("sudo /bin/cat /var/log/syslog > /tmp/syslog");
$result = shell_exec("/usr/bin/tail -3000 /tmp/syslog");
echo "<pre>". $result. "</pre>";
exec("/bin/rm /tmp/syslog");
?>
