<?php
$BASEDIR = "/home/pi/mrd-repo/mrd";
#ini_set("auto_detect_line_endings", true);
$mail = shell_exec("sed -n \"s/id: //p\" $BASEDIR/configuration.ini");
$name = shell_exec("sed -n \"s/name: //p\" $BASEDIR/configuration.ini");
$adhoc = shell_exec("sed -n \"s/adhoc: //p\" $BASEDIR/configuration.ini");
$language = shell_exec("sed -n \"s/language: //p\" $BASEDIR/configuration.ini");

if (strncmp($adhoc, "True", 4) == 0) {
    $adhoc = "Ja";
} else {
    $adhoc = "Nein";
}

if (strncmp($language, "de", 2) == 0) {
    $language = "Deutsch";
} else {
    $language = "Englisch";
}

if (strlen($mail) > 0) {
    echo "<br>";
    echo "<h3><font color='#172e67'>Aktuelle Konfiguration</font></h3>";
    echo "<table>
            <tr><td width='230px'>E-Mail:</td><td>$mail</td></tr>
            <tr><td width='230px'>Name:</td><td>$name</td></tr>
            <tr><td width='230px'>Sprache:</td><td>$language</td></tr>
            <tr><td width='230px'>Adhoc Buchungen:</td><td>$adhoc</td></tr>
          </table>";
}
?>