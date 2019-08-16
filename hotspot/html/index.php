<!DOCTYPE html>
<html lang="en">
	<!-- HTTP_HEAD -->
	<head>
		<meta name=\"mrd\" content=\"width=device-width, initial-scale=1, user-scalable=no\"/>
		<title>mrd</title>
	    <!-- HTTP_STYLE -->
		<style>
			.c{text-align: center;}
			div,input{padding:5px;font-size:1em;}
			input{width:95%;}
			body{text-align: center;font-family:verdana;}
			button{border:0;border-radius:0.3rem;background-color:#1fa3ec;color:#fff;line-height:2.4rem;font-size:1.2rem;width:100%;}
	                    .q{float: right;width: 64px;text-align: right;}
	                    h2{
	                        text-align: center;
	                        width:100%;
	                    }
		</style>
		<!-- /HTTP_STYLE -->
	</head>
	<!-- HTTP_HEAD_END -->
	<!-- HTTP_BODY -->
	<body>
        <div style="text-align:left;display:inline-block;min-width:260px;">

	        <!-- HTTP_IMG  -->
	        <p style="text-align:center;"><img src="mp.png"></p>
	        <h2><a href="/" style="text-decoration:none;color:black;text-align:center">Meeting Room Display Einrichtungsassistent</a></h2>
	        <!-- /HTTP_IMG  -->

            <h3><font color="#172e67">Netzwerk hinzufügen</font></h3>

			<!-- HTTP_FORM_START -->
	        <form method='POST' action='add_ssid.php'>
                <input id='ssid' name='ssid' length=32 placeholder='SSID'><br/>
                <input id='pwd' name='pwd' length=64 type='password' placeholder='Passwort (mind. 8 Zeichen)'><br/>
                <?php
                    if (!empty($_GET['add'])) {
                        echo "<br/>";

                        $ret = $_GET['add'];
                        $ssid = $_GET['ssid'];

                        if (strcmp($ret, "not_set") == 0) {
                            #no ssid given
                            echo "<span style='color: red;'/><center> Keine SSID angegeben, bitte erneut versuchen </center></span>";
                        } else if (strcmp($ret, "too_short") == 0) {
                            #pw is too short (at least 8)
                            echo "<span style='color: red;'/><center> Passwort für '$ssid' ist zu kurz </center></span>";
                            echo "<span style='color: red;'/><center> Bitte mindestens 8 Zeichen eingeben </center></span>";
                        } else if (strcmp($ret, "success") == 0) {
                            #everything worked out
                            echo "<span style='color: green;'/><center> SSID '$ssid' erfolgreich hinzugefügt </center></span>";
                        }
                    }
                ?>
                <br/>
                <button type='submit'>speichern</button>
            </form>
			<!-- /HTTP_FORM_END -->

			<br/><h3><font color="#172e67">Netzwerk entfernen</font></h3>

			<!-- HTTP_FORM_START -->
	        <form method='POST' action='rem_ssid.php'>
                <!--<input id='ssid' name='ssid' length=32 placeholder='remove SSID'><br/>-->
                <select name="ssid">
                <?php include ("find_ssid.php"); ?>
                </select>
                <?php
                    if (!empty($_GET['rem'])) {
                        echo "<br/>";
                        echo "<br/>";

                        $ret = $_GET['rem'];
                        $ssid = $_GET['ssid'];

                        if (strcmp($ret, "not_found") == 0) {
                            #ssid not in list
                            echo "<span style='color: red;'/><center> SSID '$ssid' nicht vorhanden </center></span>";
                        } else if (strcmp($ret, "success") == 0) {
                            #everything worked out
                            echo "<span style='color: green;'/><center>SSID '$ssid' erfolgreich entfernt </center></span>";
                        }
                    }
                ?>
                <br/>
                <br/>
                <button type='submit'>entfernen</button>
            </form>
            <!-- /HTTP_FORM_END -->

            <?php include ("current_mail.php"); ?>

			<br/><h3><font color="#172e67">Konfiguration ändern</font></h3>

            <!-- HTTP_FORM_START -->
	        <form method='POST' action='add_config.php'>
                <input id='mail' name='mail' length=64 placeholder='E-Mail'><br/>
                <input id='name' name='name' length=64 placeholder='Name'><br/>
                <input id='password' name='password' length=32 type='password' placeholder='Passwort'>

                <br/>
                <br/>

                <table>
                    <tr>
                        <td width='230px'>Display Sprache wählen:</td>
                        <td width='230px'>
                            <select id='language' name='language' placeholder='language' style='width: 120px'>
                                <option value="de">Deutsch</option>
                                <option value="en">Englisch</option>
                            </select>
                        </td>
                    </tr>
                    <tr>
                        <td width='230px'>Erlaube adhoc Meetings:</td>
                        <td width='230px'>
                            <select id='adhoc' name='adhoc' placeholder='adhoc' style='width: 120px'>
                                <option value="True">Ja</option>
                                <option value="False">Nein</option>
                            </select>
                        </td>
                    </tr>
                </table>

                <?php
                    if (!empty($_GET['mail'])) {
                        echo "<br/>";

                        $ret = $_GET['ret'];

                        if (strcmp($ret, "no_mail") == 0) {
                            #no mail given
                            echo "<span style='color: red;'/><center> E-Mail nicht gesetzt </center></span>";
                        } else if (strcmp($ret, "no_name") == 0) {
                            #no name given
                            echo "<span style='color: red;'/><center> Name nicht gesetzt </center></span>";
                        } else if (strcmp($ret, "no_password") == 0) {
                            #no password given
                            echo "<span style='color: red;'/><center> Passwort nicht gesetzt </center></span>";
                        } else if (strcmp($ret, "success") == 0) {
                            #everything worked out
                            echo "<span style='color: green;'/><center> Konfiguration erfolgreich geändert </center></span>";
                        }
                    }
                ?>

                <br/>
                <button type='submit'>speichern</button>
            </form>
			<!-- /HTTP_FORM_END -->

            <br/><h3><font color="#172e67">Hotspot beenden und Raspberry Pi neu starten</font></h3>

            <!-- HTTP_FORM_START -->
	        <form method='POST' action='wifi.php'>
                <button type='submit'>beenden</button>
            </form>
			<!-- /HTTP_FORM_END -->

		</div>
	</body>
   <!-- HTTP_BODY_END -->
</html>
