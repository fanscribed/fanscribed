<%inherit file="base.mako" />

<%def name="head_title()">Transcript</%def>

<%def name="body_class()">view</%def>

<%def name="player_update_interval()">500</%def>

<%def name="head_script()">
  <script type="text/javascript">
    $(view_onload);
  </script>
</%def>

<%def name="toolbar()">
  <strong>View</strong>
  |
  <a href="${request.route_path('edit')}">Transcribe</a>
</%def>

<%def name="sidebar_top()">
    <div id="links">
      <%
      links = transcription_info.get('links', [])
      %>
      % if links:
          <h2>Links</h2>
          <ul>
            % for link_info in transcription_info.get('links', []):
                <li><a href="${link_info['url']}">${link_info['title']}</a></li>
            % endfor
          </ul>
      % endif
    </div>
</%def>

<%def name="sidebar()">
</%def>

<%def name="body()">
  <h2>Transcript</h2>

  <div id="inline-editor-template" style="display:none;">
    <div class="inline-editor-buttons">
      <div>
        <input class="editor-save" type="button" value="Save" onclick="inline_editor_save();" />
        <input class="editor-cancel" type="button" value="Cancel" onclick="inline_editor_cancel();" />
        </div>
      <div>Special keys: \ (backslash) play/pause, ~ (tilde) replay, ` (backtick) back 5 seconds</div>
    </div>
    <textarea class="inline-editor"></textarea>
    <div class="inline-editor-instructions">
      <h3>Transcription Instructions</h3>
      <p>Listen to the audio snippet and transcribe it using the following format.</p>
      <pre>abbr; transcription of speaker</pre>
      <p>The snippet is locked for you for 20 minutes, or until you save or cancel.</p>
    </div>
  </div>

  % for starting_point, lines in snippets:
      <%
      last_speaker = None
      starting_seconds = starting_point / 1000
      starting_minutes = starting_seconds / 60
      starting_seconds = starting_seconds % 60
      anchor = '{0:d}m{1:02d}s'.format(starting_minutes, starting_seconds)
      anchor_label = '{0:d}:{1:02d}'.format(starting_minutes, starting_seconds)
      %>
      <div class="snippet" id="${anchor}">
        <p class="timestamp"><span class="label">${anchor_label}</span> - <a href="#${anchor}">#</a> - <a href="#${anchor}" onclick="player_play_from(${starting_point})">Play</a><span class="needs-identity"><span class="inline-edit-link"> - <a href="#${anchor}" onclick="inline_editor('${anchor}', ${starting_point})">Edit</a></span></span></p>
        <dl class="transcript">
          % for speaker, spoken in lines:
              % if speaker and last_speaker != speaker:
                  <dt>${speaker}:</dt>
                  <dd>${spoken}</dd>
              % else:
                  <dd>${spoken}</dd>
              % endif
              <%
                  last_speaker = speaker
              %>
          % endfor
        </dl>
        <div class="inline-editor-container" style="display:none;"></div>
      </div>
  % endfor
</%def>
