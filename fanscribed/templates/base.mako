<!DOCTYPE html>
<html>
<head>
  <title>${next.head_title()} - ${transcription_info['title']} - Fanscribed</title>
  <meta http-equiv="Content-Type" content="text/html;charset=UTF-8"/>
  <meta name="keywords" content="transcription transcribe podcast crowdsource" />
  <meta name="description" content="Croudsourced podcast transcription" />
  <link rel="shortcut icon" href="${request.static_url('fanscribed:static/favicon.ico')}?2012012401" />
  <link rel="stylesheet" href="${request.static_url('fanscribed:static/fanscribed.css')}?2012021002" type="text/css" media="screen" charset="utf-8" />
  % if custom_css_revision:
    <link rel="stylesheet" href="${request.route_path('custom_css')}?${custom_css_revision}${'&rev={0}'.format(request.GET.get('rev')) if request.GET.get('rev') else ''}" type="text/css" media="screen" charset="utf-8" />
  % endif
  <!--[if lte IE 6]>
  <link rel="stylesheet" href="${request.static_url('fanscribed:static/ie6.css')}?2012012401" type="text/css" media="screen" charset="utf-8" />
  <![endif]-->
  <script src="//ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js" type="text/javascript"></script>
</head>
<body class="${next.body_class()}">

  <div id="siteheader">
    <%
        site_name = transcription_info.get('site_name')
        site_url = transcription_info.get('site_url')
    %>
    % if site_name and site_url:
        <h3 id="header" class="headertext"><a href="${site_url}" title="${site_name}">${site_name}</a></h3>
    % else:
        <h3 id="header" class="headertext">Crowdsourced Podcast Transcription</h3>
    % endif
    <div id="subhead" class="headertext">powered by <a href="http://fanscribed.com/" title="Fanscribed">Fanscribed</a></div>
  </div>

  <div id="sidebar">
    <!--[if IE]>
    <p style="font-size:x-large;color:red;font-weight:bold;">Sorry, audio playback and transcription editing do not yet work with Internet Explorer.  Please use <a href="http://chrome.google.com/">Chrome</a>, <a href="http://getfirefox.com/">Firefox</a>, or <a href="http://apple.com/safari/">Safari</a> to hear audio or to help transcribe.  <em>If you are a web developer, please <a href="https://github.com/fanscribed/fanscribed/issues/26">help solve IE compatibility issues</a>.</em></p>
    <![endif]-->

    <div id="links">
      <%
      links = transcription_info.get('links', [])
      %>
      % if links:
          <h2>Links</h2>
          <ul>
            % for link_info in transcription_info.get('links', []):
                <li><a href="${link_info['url']}" target="_blank">${link_info['title']}</a></li>
            % endfor
          </ul>
      % endif
    </div>

    ${next.sidebar_top()}

    <div id="speakers" class="hidden-while-viewing needs-identity no-identity needs-player no-player">
      <h2>Speaker Abbreviations</h2>

      <div>
        <input id="speakers-edit" type="button" value="Edit" onclick="edit_speakers();" />
        <input id="speakers-save" style="display: none;" type="button" value="Save" onclick="save_speakers();" />
        <input id="speakers-cancel" style="display: none;" type="button" value="Cancel" onclick="cancel_speakers();" />
      </div>

      <pre id="speakers-text">${speakers}</pre>
      <textarea id="speakers-editor" style="display: none;"></textarea>

      <div id="instructions-speakers" style="display: none;">
        <p>Add speaker abbreviations one per line, in this format:</p>
        <pre>abbr; Full Name</pre>
        <p>Be sure to <strong>save right away</strong> to prevent conflicts between concurrent changes. Unlike the transcription editor below, the list of speakers is <strong>not locked</strong>.</p>
      </div>
    </div>

    <div id="progress">
      <h2>Progress</h2>
      <ul>
        <li style="${'display: none;' if 'duration' in transcription_info else ''}">Initialized: <span id="about-initialized">${'true' if 'duration' in transcription_info else 'false'}</span></li>
        <li>
          Snippets transcribed: 
          <span id="snippets-progress-percent"><span style="width:${snippets_progress['percent']}%"><strong>${snippets_progress['percent']}%</strong></span></span> 
          (<span id="snippets-progress-completed">${snippets_progress['completed']}</span> out of <span id="snippets-progress-total">${snippets_progress['total']}</span>)
        </li>
        <li>
          Reviews completed: 
          <span id="reviews-progress-percent"><span style="width:${reviews_progress['percent']}%"><strong>${reviews_progress['percent']}%</strong></span></span>
          (<span id="reviews-progress-completed">${reviews_progress['completed']}</span> out of <span id="reviews-progress-total">${reviews_progress['total']}</span>)
        </li>
      </ul>
    </div>

    ${next.sidebar()}

    <div id="player-info" class="needs-player no-player">
      <h2>Player</h2>
      <ul>
        <li><input id="player-auto-play-edit" type="checkbox"> <label for="player-auto-play-edit">Auto-play (on edit)</label></li>
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
    <div id="title">
      <h1 id="about-title">${transcription_info['title']}</h1>
    </div>

    ${next.preamble()}

    <ul id="toolbar">
      ${next.toolbar()}
    </ul>

    ${next.body()}
  </div>

  <div id="footer">
    <div class="footer">Transcript content is subject to copyrights held by its creators.</div>
  </div>

  % if not request.GET.get('noflash') == '1':
      <object id="player" type="application/x-shockwave-flash" data="${request.static_url('fanscribed:static/player_mp3_js.swf')}" width="1" height="1">
        <param name="AllowScriptAccess" value="always">
        <param name="FlashVars" value="listener=player_listener&amp;interval=${next.player_update_interval()}">
      </object>
  % endif

  <script type="text/javascript" src="${request.static_url('fanscribed:static/jquery.cookie.js')}?2012012401"></script>
  <script type="text/javascript" src="${request.static_url('fanscribed:static/fanscribed.js')}?2012021301"></script>
  <script type="text/javascript">
    var cookie_options = {
      expires: 365,
      path: '/',
      // TLD generated by stripping extra subdomains and trailing ports
      domain: '${('.'.join((request.host.split('.'))[-2:])).split(':', 1)[0]}'
    };
    var transcription = ${transcription_info_json | n};
    var latest_revision = '${latest_revision}';
  </script>
  ${next.head_script()}
  % if custom_js_revision:
    <script type="text/javascript" src="${request.route_path('custom_js')}?${custom_js_revision}${'&rev={0}'.format(request.GET.get('rev')) if request.GET.get('rev') else ''}"></script>
  % endif
  ${tracking_html | n}

</body>
</html>
