<%inherit file="base.mako" />

<%def name="head_title()">Transcription</%def>

<%def name="player_update_interval()">500</%def>

<%def name="head_script()">
  <script type="text/javascript">
    $(view_onload);
  </script>
</%def>

<%def name="toolbar()">
  <strong>View</strong>
  |
  <a href="${request.route_path('edit')}">Edit</a>
</%def>

<%def name="body()">
  <h1>Speakers</h1>

  <pre id="speakers-text"></pre>

  <h1>Transcription</h1>

  % for starting_point, lines in snippets:
      <div>
        <p><a id="s${starting_point}" href="#s${starting_point}">${starting_point / 1000} seconds</a></p>
        % for left, right in lines:
            % if left:
                <p>${left}: ${right}</p>
            % else:
                <p>${line}</p>
            % endif
        % endfor
      </div>
  % endfor
</%def>
