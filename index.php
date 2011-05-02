<?php
// generate session and token
require_once 'API_Config.php';
require_once 'OpenTokSDK.php';

$apiObj = new OpenTokSDK(API_Config::API_KEY, API_Config::API_SECRET);
$session = $apiObj->create_session($_SERVER["REMOTE_ADDR"]);

?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
	<head>
		<title>Spin Cycle</title>
		<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
		<script type="text/javascript" src="jquery-1.5.1.min.js"></script>
		<script type="text/javascript" src="swfobject.js"></script>
		<script type="text/javascript">
			var flashvars = {
				"session": "<?php print $session->getSessionId(); ?>",
				"token": "<?php print $apiObj->generate_token(); ?>"
			};

			var params = {};

			params.allowscriptaccess = "always";
			var attributes = {};
			swfobject.embedSWF("spin2.swf", "spincycle", "1390", "623", "10.0.0", false, flashvars, params, attributes);


			// gets called from flash once everything's loaded
			var callback = function() {
				$('#curtain').fadeOut(); // comment out this line to see loading image
			};
		</script>
		<style type="text/css">
			html, body {
				font-family: Helvetica, Verdana, Arial, sans-serif;
				margin: 0;
				padding: 0;
				width: 100%;
				height: 100%;
				overflow: hidden;
				background-color: #294642;
			}

			div#background {
				position: relative;
				width: 100%;
				height: 100%;
				background-color: #294642;
			}

			div#stage {
				position:absolute;
				width: 1390px;
				height: 623px;
				left: 50%;
				top: 50%;
				margin: -311px 0 0 -695px;
				background: black;
				border: 6px solid #688f83;
			}

			div#curtain {
				position: absolute;
				left: 0;
				top: 0;
				background-color: #294642;
				width: 100%;
				height: 100%;
				color: white;


			}

			div#loading-message {
				position: relative;
				top: 50%;
				width: 300px;
				height: 200px;
				margin: -100px auto 0 auto;
				text-align: center;
				font-weight: bold;
			}



		</style>

	</head>
	<body>
		<div id="background">
			<div id="stage">
				<div id="spincycle">
					<a href="http://www.adobe.com/go/getflashplayer">
					<img src="http://www.adobe.com/images/shared/download_buttons/get_flash_player.gif" alt="Get Adobe Flash player" />
					</a>
				</div>
			</div>
		</div>
		<div id="curtain">
			<div id="loading-message">
			Loading<br /><br />
			Come take it for a spin!
			</div>
		</div>
	</body>
</html>
