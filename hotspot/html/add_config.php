<?php
$mail = $_POST["mail"];
$name = $_POST["name"];
$password = $_POST["password"];
$adhoc = $_POST["adhoc"];
$language = $_POST["language"];

if (strlen($mail) == 0) {
    $ret = "no_mail";
} else if (strlen($name) == 0) {
    $ret = "no_name";
} else if (strlen($password) == 0) {
    $ret = "no_password";
} else {
    shell_exec("/bin/bash add_config.sh '${mail}' '${name}' '${password}' '${adhoc}' '${language}' >/dev/null 2>&1");
    $ret = "success";
}
header("Location: index.php?mail=$mail&ret=$ret");
exit();
?>
