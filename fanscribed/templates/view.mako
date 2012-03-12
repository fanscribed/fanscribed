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
  <li class="tab view"><span>Read</span></li>
  <li class="tab transcribe"><a href="${request.route_path('edit')}" title="Transcribe">Transcribe</a></li>
</%def>

<%def name="sidebar_top()">
</%def>

<%def name="sidebar()">
</%def>

<%def name="preamble()">
  % if snippets_progress['percent'] == 100:
      % if preamble_completed:
          <div id="preamble">
            ${preamble_completed|n}
          </div>
      % endif
  % else:
      % if preamble_incomplete:
          <div id="preamble">
            ${preamble_incomplete|n}
          </div>
      % endif
  % endif
</%def>

<%def name="body()">
  <h2 id="contentheader">Transcript</h2>

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

  <div id="snippet-info-template" class="snippet-info" style="display:none;">
    <div class="contributors">
      Contributors (by date):
      <ul class="contributor-list" />
    </div>
  </div>

  <%
  last_abbreviation = ''
  %>
  % for starting_point, lines in snippets:
      <%
      # Reset last_abbreviation if an empty snippet is found.
      if not lines:
          last_abbreviation = ''
      starting_seconds = starting_point / 1000
      starting_minutes = starting_seconds / 60
      starting_seconds = starting_seconds % 60
      anchor = '{0:d}m{1:02d}s'.format(starting_minutes, starting_seconds)
      anchor_label = '{0:d}:{1:02d}'.format(starting_minutes, starting_seconds)
      %>
      <div class="snippet" id="${anchor}">
        <ul class="timestamp">
          <li class="label"><a href="#${anchor}">${anchor_label}</a></li>
          <li class="play needs-player no-player"><a href="#${anchor}">Play</a></li>
          <li class="edit needs-identity no-identity needs-player no-player"><a href="#${anchor}" onclick="inline_editor('${anchor}', ${starting_point})">Edit</a></li>
          <li class="info"><a href="#${anchor}" onclick="show_snippet_info('${anchor}', ${starting_point})">Info</a></li>
        </ul>
        <div class="snippet-info-container"></div>
        <dl class="transcript">
          % for abbreviation, speaker, spoken in lines:
              % if abbreviation and last_abbreviation != speaker:
                  <dt class="speaker-${abbreviation}"><span class="name">${speaker}</span>:</dt>
                  <%
                      last_abbreviation = abbreviation
                  %>
              % endif
              <dd class="speaker-${last_abbreviation}">${spoken}</dd>
          % endfor
        </dl>
        <div class="inline-editor-container" style="display:none;"></div>
      </div>
  % endfor
</%def>
