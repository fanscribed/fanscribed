<%inherit file="base.mako" />

<%def name="head_title()">Transcription</%def>

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
