<!-- HTTP_HEAD -->
<!DOCTYPE html>
<html lang="en">
	<!-- /HTTP_HEAD -->
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
                            width:100%
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
            <h2 class="headertekst"><a href="/" style="text-align:center;text-decoration:none;color:black">Raspberry Pi Neustart</a></h2>
		    <!-- /HTTP_IMG  -->

            <?php
            echo "<br/>";
            echo "<span style='color: red;'/><center>Meeting Room Display wird neu gestartet</center></span>";
            echo "<br/>";
            echo "<span style='color: red;'/><center>Verbindung zum Netzwerk wird hergestellt</center></span>";
            echo "<span style='color: red;'/><center>Hotspot ist unerreichbar</center></span>";
            echo "<span style='color: red;'/><center>Dies kann einige Sekunden dauern</center></span>";
            echo "<br/>";
            ?>

            <?php header('Refresh: 3; URL=https://methodpark.de');?>
        </div>
    </body>
	<!-- HTTP_BODY_END -->
</html>
