<%inherit file="base.mako" />

<%def name="head_title()">Edit Transcription</%def>

<%def name="head_script()">
  <script type="text/javascript">
    $(edit_onload);
  </script>
</%def>

<%def name="toolbar()">
  <p>
    <a href="${request.route_path('view')}">View</a>
    |
    <strong>Edit</strong>
  </p>

  <ul>
    <li>Name: <input id="identity-name" type="text" /></li>
    <li>Email: <input id="identity-email" type="text" /></li>
    <li><input id="identity-save" type="button" value="Save" onclick="save_identity();" /> <span id="identity-saved" /></li>
  </ul>
</%def>
