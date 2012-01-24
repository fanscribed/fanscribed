<%inherit file="base.mako" />

<%def name="head_title()">Edit Transcription</%def>

<%def name="player_update_interval()">200</%def>

<%def name="head_script()">
  <script type="text/javascript">
    $(edit_onload);
  </script>
</%def>

<%def name="toolbar()">
  <p>
    <a href="${request.route_path('view')}">View</a>
    |
    <strong>Transcribe</strong>
  </p>

  <ul>
    <li>Name: <input id="identity-name" type="text" /></li>
    <li>Email: <input id="identity-email" type="text" /></li>
    <li><input id="identity-save" type="button" value="Save" onclick="save_identity();" /> <span id="identity-saved" /></li>
  </ul>
</%def>

<%def name="body()">
  <div id="speakers">
    <h1>Speakers</h1>

    <div id="instructions-speakers" style="display: none;">
      <p>Add speaker abbreviations one per line, in this format:</p>
      <pre>abbr; Full Name</pre>
      <p>Be sure to <strong>save right away</strong> to prevent conflicts between concurrent changes. Unlike the transcription editor below, the list of speakers is <strong>not locked</strong>.</p>
    </div>

    <pre id="speakers-text">${speakers}</pre>
    <textarea id="speakers-editor" style="display: none;"></textarea>

    <p>
      <input id="speakers-edit" type="button" value="Edit" onclick="edit_speakers();" />
      <input id="speakers-save" style="display: none;" type="button" value="Save" onclick="save_speakers();" />
      <input id="speakers-cancel" style="display: none;" type="button" value="Cancel" onclick="cancel_speakers();" />
    </p>
  </div>

  <div>
    <h1>Editor</h1>

    <p>Editing: <span id="editing">Nothing</span></p>

    <p id="edit-buttons">
      <input id="editor-transcribe" type="button" value="Transcribe" onclick="editor_transcribe();" />
      <input id="editor-review" type="button" value="Review" onclick="editor_review();" />
    </p>

    <div id="instructions-transcribe" style="display: none;">
      <p>Listen to the audio snippet and transcribe it using the following format.</p>
      <pre>abbr; transcription of speaker</pre>
      <p>The snippet is locked for you for 20 minutes, or until you save or cancel.</p>
      <p>Special keys: \ (backslash) play/pause, ~ (tilde) replay, ` (backtick) back 5 seconds</p>
    </div>

    <div id="instructions-review" style="display: none;">
      <p>Listen to the combined audio snippets, and review and correct the transcriptions using the following format.</p>
      <pre>abbr; transcription of speaker</pre>
      <p>In particular, if a transcription is duplicated or split between the end of the first and the beginning of the second, move the text to one snippet or the other to rectify. <em>Do not worry about words missing from the beginning of the first snippet or the end of the second,</em> as that is likely a side-effect of someone else reviewing that snippet adjacent to one you cannot see.</p>
      <p>The snippets are locked for you for 20 minutes, or until you save or cancel.</p>
      <p>Special keys: \ (backslash) play/pause, ~ (tilde) replay, ` (backtick) back 5 seconds</p>
    </div>

    <textarea class="player-shortcuts" id="transcribe-editor" style="display: none;"></textarea>
    <textarea class="player-shortcuts" id="review-editor1" style="display: none;"></textarea>
    <textarea class="player-shortcuts" id="review-editor2" style="display: none;"></textarea>

    <p id="edit-action-buttons" style="display: none;">
      <input id="editor-save" type="button" value="Save" onclick="editor_save();" />
      <input id="editor-cancel" type="button" value="Cancel" onclick="editor_cancel();" />
      <input id="editor-replay" type="button" value="Replay" onclick="editor_replay();" />
      <input id="editor-pause" type="button" value="Pause/Play" onclick="editor_pause_play();" />
      <input id="editor-rewind" type="button" value="Rewind 5s" onclick="editor_rewind();" />
    </p>
  </div>
</%def>
