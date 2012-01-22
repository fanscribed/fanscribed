<!DOCTYPE html>
<html>
<head>
  <title>${next.head_title()} - ${transcription_info['title']} - Fanscribed</title>
  <meta http-equiv="Content-Type" content="text/html;charset=UTF-8"/>
  <meta name="keywords" content="transcription transcribe podcast crowdsource" />
  <meta name="description" content="Croudsourced podcast transcription" />
  <link rel="shortcut icon" href="${request.static_url('fanscribed:static/favicon.ico')}" />
  <link rel="stylesheet" href="${request.static_url('fanscribed:static/fanscribed.css')}" type="text/css" media="screen" charset="utf-8" />
  <!--[if lte IE 6]>
  <link rel="stylesheet" href="${request.static_url('fanscribed:static/ie6.css')}" type="text/css" media="screen" charset="utf-8" />
  <![endif]-->
  <script src="//ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js" type="text/javascript"></script>
  <script type="text/javascript" src="${request.static_url('fanscribed:static/jquery.cookie.js')}"></script>
  <script type="text/javascript" src="${request.static_url('fanscribed:static/fanscribed.js')}"></script>
  <script type="text/javascript">
    var cookie_options = {
      expires: 365,
      path: '/',
      domain: '${'.'.join((request.host.split('.'))[-2:])}'
    };
    var transcription = ${transcription_info_json | n};
  </script>
  ${next.head_script()}
</head>
<body>

  <div id="toolbar">
    ${next.toolbar()}
  </div>

  <div id="about">
    <h1>About</h1>
    <ul>
      <li>Title: <span id="about-title">${transcription_info['title']}</span></li>
      <li>Homepage: <a id="about-homepage" href="${transcription_info['homepage_url']}">${transcription_info['homepage_url']}</a></li>
      <li>Audio: <a id="about-audio" href="${transcription_info['audio_url']}">${transcription_info['audio_url']}</a></li>
      <li>Initialized: <span id="about-initialized">${'true' if 'duration' in transcription_info else 'false'}</span></li>
    </ul>
  </div>

  ${next.body()}

  <div id="player-info">
    <h1>Player</h1>
    <ul>
      <li>enabled: <span id="player-enabled"></span></li>
      <li>isPlaying: <span id="player-isPlaying"></span></li>
      <li>url: <span id="player-url"></span></li>
      <li>volume: <span id="player-volume"></span></li>
      <li>position: <span id="player-position"></span> (<span id="player-position-minutes"></span> minutes)</li>
      <li>duration: <span id="player-duration"></span> (<span id="player-duration-minutes"></span> minutes)</li>
      <li>bytesLoaded: <span id="player-bytesLoaded"></span></li>
      <li>bytesTotal: <span id="player-bytesTotal"></span></li>
    </ul>
  </div>

  <div id="footer">
    <div class="footer">Fanscribed &copy; Copyright 2012, <a href="http://11craft.com/">ElevenCraft Inc.</a></div>
  </div>

  <object id="player" type="application/x-shockwave-flash" data="${request.static_url('fanscribed:static/player_mp3_js.swf')}" width="1" height="1">
    <param name="AllowScriptAccess" value="always">
    <param name="FlashVars" value="listener=player_listener&amp;interval=${next.player_update_interval()}">
  </object>
</body>
</html>
