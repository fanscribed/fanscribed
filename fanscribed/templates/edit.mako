<%inherit file="base.mako" />

<%def name="head_title()">Edit Transcription</%def>

<%def name="head_script()">
  <script type="text/javascript">
    $(edit_onload);
  </script>
</%def>

<%def name="toolbar()">
  <a href="${request.route_path('view')}">View</a>
  |
  <strong>Edit</strong>
</%def>
