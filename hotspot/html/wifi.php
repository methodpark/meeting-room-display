<?php

header("Location: restart.php");

exec("/bin/bash wifi.sh > /dev/null 2>&1 &");

exit();
?>
