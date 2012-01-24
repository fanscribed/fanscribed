<!DOCTYPE html>
<html>
<head>
  <title>${next.head_title()} - ${transcription_info['title']} - Fanscribed</title>
  <meta http-equiv="Content-Type" content="text/html;charset=UTF-8"/>
  <meta name="keywords" content="transcription transcribe podcast crowdsource" />
  <meta name="description" content="Croudsourced podcast transcription" />
  <link rel="shortcut icon" href="${request.static_url('fanscribed:static/favicon.ico')}?2012012401" />
  <link rel="stylesheet" href="${request.static_url('fanscribed:static/fanscribed.css')}?2012012401" type="text/css" media="screen" charset="utf-8" />
  <!--[if lte IE 6]>
  <link rel="stylesheet" href="${request.static_url('fanscribed:static/ie6.css')}?2012012401" type="text/css" media="screen" charset="utf-8" />
  <![endif]-->
  <script src="//ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js" type="text/javascript"></script>
  <script type="text/javascript" src="${request.static_url('fanscribed:static/jquery.cookie.js')}?2012012401"></script>
  <script type="text/javascript" src="${request.static_url('fanscribed:static/fanscribed.js')}?2012012401"></script>
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
<body class="${next.body_class()}">

  <div id="toolbar">
    ${next.toolbar()}
  </div>

  <div id="title">
    <h1 id="about-title">${transcription_info['title']}</h1>
  </div>

  <div id="sidebar">
    <!--[if IE]>
    <p style="font-size:x-large;color:red;font-weight:bold;">Sorry, audio playback and transcription editing do not yet work with Internet Explorer.  Please use <a href="http://chrome.google.com/">Chrome</a>, <a href="http://getfirefox.com/">Firefox</a>, or <a href="http://apple.com/safari/">Safari</a> to hear audio or to help transcribe.</p>
    <![endif]-->

    ${next.sidebar_top()}

    <div id="progress">
      <h2>Progress</h2>
      <ul>
        <li style="${'display: none;' if 'duration' in transcription_info else ''}">Initialized: <span id="about-initialized">${'true' if 'duration' in transcription_info else 'false'}</span></li>
        <li>Snippets transcribed: <span id="snippets-progress-percent">${snippets_progress['percent']}</span>% (<span id="snippets-progress-completed">${snippets_progress['completed']}</span> out of <span id="snippets-progress-total">${snippets_progress['total']}</span>)</li>
        <li>Reviews completed: <span id="reviews-progress-percent">${reviews_progress['percent']}</span>% (<span id="reviews-progress-completed">${reviews_progress['completed']}</span> out of <span id="reviews-progress-total">${reviews_progress['total']}</span>)</li>
      </ul>
    </div>

    ${next.sidebar()}

    <div id="player-info">
      <h2>Player</h2>
      <ul>
        <li style="display:none;">enabled: <span id="player-enabled"></span></li>
        <li>playing: <span id="player-isPlaying"></span></li>
        <li style="display:none;">url: <span id="player-url"></span></li>
        <li style="display:none;">volume: <span id="player-volume"></span></li>
        <li>position: <span id="player-position"></span></li>
        <li>duration: <span id="player-duration"></span></li>
        <li>bytes loaded: <span id="player-bytesLoaded"></span></li>
        <li>bytes total: <span id="player-bytesTotal"></span></li>
      </ul>
    </div>
  </div>

  <div id="content">
    ${next.body()}
  </div>

  <div id="footer">
    <div class="footer">Powered by <a href="http://fanscribed.com/">Fanscribed</a>, &copy; 2012 by <a href="http://11craft.com/">ElevenCraft</a>. Site content is subject to copyrights held by its creators.</div>
  </div>

  <object id="player" type="application/x-shockwave-flash" data="${request.static_url('fanscribed:static/player_mp3_js.swf')}" width="1" height="1">
    <param name="AllowScriptAccess" value="always">
    <param name="FlashVars" value="listener=player_listener&amp;interval=${next.player_update_interval()}">
  </object>
</body>
</html>
