<%inherit file="base.mako" />

<%def name="head_title()">Edit Transcription</%def>

<%def name="body_class()">edit</%def>

<%def name="player_update_interval()">200</%def>

<%def name="head_script()">
  <script type="text/javascript">
    $(edit_onload);
  </script>
</%def>

<%def name="toolbar()">
  <li class="tab view"><a href="${request.route_path('view')}" title="Read">Read</a></li>
  <li class="tab transcribe"><span>Transcribe</span></li>
</%def>

<%def name="sidebar_top()">
  <div id="quickstart">
    <h2>Quick Start</h2>
    <p>Set your identity below. Click "Transcribe" or "Review" on the left. Follow the instructions that appear. If you don't hear audio right away, see "Player" below &mdash; it's probably still buffering.</p>
  </div>
</%def>

<%def name="sidebar()">
  <div id="identity" class="needs-player no-player">
    <h2>Identity</h2>
    <div>For giving you credit for your work.</div>
    <ul>
      <li>Name: <input id="identity-name" type="text" /></li>
      <li>Email: <input id="identity-email" type="text" /></li>
      <li><input id="identity-save" type="button" value="Save" onclick="save_identity();" /> <span id="identity-saved" /></li>
    </ul>
  </div>
</%def>

<%def name="body()">
  <h2 id="contentheader">Transcription and Review Tools</h2>

  <p class="needs-unset-player">
    Getting the player ready.
    If this message does not disappear, please make sure you enable Flash to use editing and playback features.
  </p>

  <p class="needs-unset-identity no-unset-identity">
    Please see the <em>Quick Start</em> to the right to continue.
  </p>

  <div class="needs-identity no-identity needs-player no-player">
    <h2>Editing: <span id="editing">Nothing</span></h2>

    <div id="edit-buttons">
      <input id="editor-transcribe" type="button" value="Transcribe" onclick="editor_transcribe();" />
      <input id="editor-review" type="button" value="Review" onclick="editor_review();" />
    </div>

    <div id="edit-action-buttons" style="display: none;">
      <div>
        <input id="editor-save-continue" type="button" value="Save &amp; continue" onclick="editor_save(true);" />
        <input id="editor-save-stop" type="button" value="Save &amp; stop" onclick="editor_save(false);" />
        <input id="editor-cancel" type="button" value="Cancel" onclick="editor_cancel();" />
      </div>
      <div>Special keys: \ (backslash) play/pause, ~ (tilde) replay, ` (backtick) back 5 seconds</div>
    </div>

    <textarea id="transcribe-editor" style="display: none;"></textarea>
    <textarea id="review-editor1" style="display: none;"></textarea>
    <textarea id="review-editor2" style="display: none;"></textarea>

    <div id="instructions-transcribe" style="display: none;">
      <h3>Transcription Instructions</h3>
      <p>Listen to the audio snippet and transcribe it using the following format.</p>
      <pre>abbr; transcription of speaker</pre>
      <p>The snippet is locked for you for 20 minutes, or until you save or cancel.</p>
    </div>

    <div id="instructions-review" style="display: none;">
      <h3>Review Instructions</h3>
      <p>Listen to the combined audio snippets, and review and correct the transcriptions using the following format.</p>
      <pre>abbr; transcription of speaker</pre>
      <p>In particular, if a transcription is duplicated or split between the end of the first and the beginning of the second, move the text to one snippet or the other to rectify. <em>Do not worry about words missing from the beginning of the first snippet or the end of the second,</em> as that is likely a side-effect of someone else reviewing that snippet adjacent to one you cannot see.</p>
      <p>The snippets are locked for you for 20 minutes, or until you save or cancel.</p>
      <p>Special keys: \ (backslash) play/pause, ~ (tilde) replay, ` (backtick) back 5 seconds</p>
    </div>

  </div>
</%def>
