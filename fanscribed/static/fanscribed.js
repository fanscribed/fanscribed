// =========================================================================
// constants


var PADDING = 2.5 * 1000; // 2.5 second audio padding on either side of a snippet
var UPDATE_SNIPPETS_INTERVAL = 3 * 60 * 1000; // check for new snippets every 3 mins


// =========================================================================
// globals (yes, I know... run away screaming!)


var latest_revision; // set in header of page
var mode; // 'view' or 'transcribe'
var transcription = {};


// =========================================================================
// onload


var edit_onload = function () {
    mode = 'transcribe';
    common_onload();
};


var view_onload = function () {
    mode = 'view';
    common_onload();
    $('.play a').click(player_play_from_snippet_start);
    start_updating_snippets();
};


var common_onload = function () {
    common_event_handlers();
    set_default_player_preferences();
    fill_player_preferences();
    fill_identity();
    check_identity_and_rev();
    player_enable();
    player_shortcuts_enable();
};


var common_event_handlers = function () {
    $('#player-auto-play-edit').change(player_auto_play_edit_changed);
};


// =========================================================================
// identity


var fill_identity = function () {
    var name = $.cookie('identity_name');
    var email = $.cookie('identity_email');
    $('#identity-name').val(name);
    $('#identity-email').val(email);
};


var save_identity = function () {
    var name = $('#identity-name').val();
    var email = $('#identity-email').val();
    $.cookie('identity_name', name, cookie_options);
    $.cookie('identity_email', email, cookie_options);
    $('#identity-saved').text('Saved!');
    var clear = function () { $('#identity-saved').text(''); };
    window.setTimeout(clear, 1000);
    check_identity_and_rev();
    return false;
};


// update UI elements based on whether identity found.
// if rev not specified or is not 'master', assume anonymous identity and present read-only behavior.
var check_identity_and_rev = function () {
    var rev_is_master = !url_params.rev || url_params.rev == 'master';
    if (has_identity(false) && rev_is_master) {
        // enable UI needing identity
        $('.needs-identity').removeClass('no-identity');
        $('.needs-unset-identity').addClass('no-unset-identity');
    } else {
        // disable UI needing identity
        $('.needs-identity').addClass('no-identity');
        $('.needs-unset-identity').removeClass('no-unset-identity');
    }
};


var has_identity = function (showAlert) {
    if (!($.cookie('identity_name')) || !($.cookie('identity_email'))) {
        if (showAlert) {
            alert('Must set identity before continuing.');
        }
      return false;
    } else {
        return true;
    }
};


// =========================================================================
// editor


var lock_info = {
    starting_point: undefined,
    ending_point: undefined,
    secret: undefined,
    type: undefined
};

var streaming_snippet = false;


var edit_speakers = function () {
    $.get(
        // url
        '/speakers.txt',
        // success
        function (data) {
            $('#speakers-editor')
                .val(data)
                .show()
            ;
            $('#speakers-edit').hide();
            $('#speakers-save').show();
            $('#speakers-cancel').show();
            $('#speakers-text').hide();
            $('#instructions-speakers').show();
        }
    );
    return false;
};


var save_speakers = function () {
    if (has_identity(true)) {
        $.post(
            // url
            '/speakers.txt',
            // data
            {
                text: $('#speakers-editor').val(),
                identity_name: $.cookie('identity_name'),
                identity_email: $.cookie('identity_email')
            },
            // success
            function (data) {
                $('#speakers-text')
                    .text(data)
                    .show()
                ;
                $('#speakers-edit').show();
                $('#speakers-save').hide();
                $('#speakers-cancel').hide();
                $('#speakers-editor').hide();
                $('#instructions-speakers').hide();
            }
        );
    }
  return false;
};


var cancel_speakers = function () {
    $.get(
        // url
        '/speakers.txt',
        // success
        function (data) {
            $('#speakers-text')
                .text(data)
                .show()
            ;
            $('#speakers-edit').show();
            $('#speakers-save').hide();
            $('#speakers-cancel').hide();
            $('#speakers-editor').hide();
            $('#instructions-speakers').hide();
        }
    );
    return false;
};


var hide_editor = function () {
    $('#edit-buttons').show();
    $('#edit-action-buttons').hide();
    $('#transcribe-editor').hide();
    $('#review-editor1').hide();
    $('#review-editor2').hide();
    $('#instructions-transcribe').hide();
    $('#instructions-review').hide();
    $('#editing').text('Nothing');
};


var editor_transcribe = function () {
    if (has_identity(true)) {
        $.post(
            // url
            '/lock_snippet',
            // data
            {
                identity_name: $.cookie('identity_name'),
                identity_email: $.cookie('identity_email')
            },
            // success
            function (data) {
                if (data.lock_acquired) {
                    lock_info.starting_point = data.starting_point;
                    lock_info.ending_point = data.ending_point;
                    lock_info.secret = data.lock_secret;
                    lock_info.type = 'snippet';
                    $('#transcribe-editor')
                        .val(data.snippet_text)
                        .show()
                        .focus()
                    ;
                    $('#edit-buttons').hide();
                    $('#edit-action-buttons').show();
                    $('#instructions-transcribe').show();
                    $('#editing').text('Transcript from ' + ms_to_label(data.starting_point) + ' to ' + ms_to_label(data.ending_point));
                    editor_replay();
                } else {
                    alert(data.message);
                    hide_editor();
                    request_and_fill_progress();
                }
            },
            // return data type
            'json'
        );
    }
  return false;
};


var editor_review = function () {
    if (has_identity(true)) {
        $.post(
            // url
            '/lock_review',
            // data
            {
                identity_name: $.cookie('identity_name'),
                identity_email: $.cookie('identity_email')
            },
            // success
            function (data) {
                if (data.lock_acquired) {
                    lock_info.starting_point = data.starting_point;
                    lock_info.ending_point = data.ending_point;
                    lock_info.secret = data.lock_secret;
                    lock_info.type = 'review';
                    $('#review-editor1')
                        .val(data.review_text_1)
                        .show()
                        .focus()
                    ;
                    $('#review-editor2')
                        .val(data.review_text_2)
                        .show()
                    ;
                    $('#edit-buttons').hide();
                    $('#edit-action-buttons').show();
                    $('#instructions-review').show();
                    $('#editing').text('Review from ' + ms_to_label(data.starting_point) + ' to ' + ms_to_label(data.ending_point));
                    editor_replay();
                } else {
                    alert(data.message);
                    hide_editor();
                    request_and_fill_progress();
                }
            },
            // return data type
            'json'
        );
    }
  return false;
};


var editor_save = function (continue_editing) {
    player_pause(true);
    if (has_identity(true)) {
        var data = {
            lock_secret: lock_info.secret,
            starting_point: lock_info.starting_point,
            identity_name: $.cookie('identity_name'),
            identity_email: $.cookie('identity_email')
        };
        var url;
        // Get appropriate text based on what's being edited.
        if (lock_info.type == 'snippet') {
            data.snippet_text = $('#transcribe-editor').val();
            url = '/save_snippet';
        } else if (lock_info.type == 'review') {
            data.review_text_1 = $('#review-editor1').val();
            data.review_text_2 = $('#review-editor2').val();
            url = '/save_review';
        } else {
            alert('Unknown lock type ' + lock_info.type);
            return false;
        }
      if (continue_editing) {
            url = url + '?continue=1';
        }
      $.post(url, data, function () {
            var lock_type = lock_info.type; // to determine what to do if user wants to continue
            lock_info.secret = undefined;
            lock_info.starting_point = undefined;
            lock_info.ending_point = undefined;
            lock_info.type = undefined;
            request_and_fill_progress();
            if (continue_editing) {
                if (lock_type == 'snippet') {
                    editor_transcribe();
                } else if (lock_type == 'review') {
                    editor_review();
                }
            } else {
                hide_editor();
            }
        });
    }
  return false;
};


var editor_cancel = function () {
    player_pause(true);
    if (has_identity(true)) {
        var data = {
            lock_secret: lock_info.secret,
            starting_point: lock_info.starting_point,
            identity_name: $.cookie('identity_name'),
            identity_email: $.cookie('identity_email')
        };
        var url;
        // Set URL based on what's being edited.
        if (lock_info.type == 'snippet') {
            url = '/cancel_snippet';
        } else if (lock_info.type == 'review') {
            url = '/cancel_review';
        } else {
            alert('Unknown lock type ' + lock_info.type);
            return false;
        }
      $.post(url, data, function () {
            lock_info.secret = undefined;
            lock_info.starting_point = undefined;
            lock_info.ending_point = undefined;
            lock_info.type = undefined;
            request_and_fill_progress();
            hide_editor();
        });
    }
  return false;
};


// set by editor_replay, and cancelled by player_pause
var wait_for_end_timeout;


var editor_replay = function (ignore_cookie) {
    // only perform replay if we've locked a snippet
    // otherwise it doesn't make sense
    if (lock_info.starting_point !== undefined && (ignore_cookie || $.cookie('auto_play_edit'))) {
        var starting_point = lock_info.starting_point;
        var length = lock_info.ending_point - lock_info.starting_point;
        // reset the player's URL
        var url = '/snippet.mp3?starting_point=' + starting_point + '&length=' + length + '&padding=' + PADDING;
        if (player_listener.url != url) {
            player().SetVariable('method:stop', '');
            player().SetVariable('method:setUrl', url);
            streaming_snippet = true;
        }
        // start playing, then stop at the end.
        player_seek(0);
        player_play();
        player_replay_at_end();
    }
  return false;
};


var editor_pause_play = function () {
    if (player_listener.isPlaying == 'true') {
        player_pause(false);
    } else {
        // seek backward 500 ms to prevent skipping over audio
        var new_position = parseFloat(player_listener.position) - 500;
        if (new_position < 0) {
            // don't go past beginning of snippet.
            new_position = 0;
        }
      player_seek(new_position);
        player_play();
    }
};


var editor_rewind = function () {
    var new_position = parseFloat(player_listener.position) - 5000;
    if (new_position < 0) {
        // don't go past beginning of snippet.
        new_position = 0;
    }
  player_seek(new_position);
    if (player_listener.isPlaying != 'true') {
        player_play();
    }
};


// =========================================================================
// inline editor


var $current_inline_editor_div;


var inline_editor = function (anchor, starting_point) {
    if (has_identity(true) && !lock_info.starting_point) {
        $.post(
            // url
            '/lock_snippet',
            // data
            {
                identity_name: $.cookie('identity_name'),
                identity_email: $.cookie('identity_email'),
                starting_point: starting_point
            },
            // success
            function (data) {
                if (data.lock_acquired) {
                    stop_updating_snippets();
                    lock_info.starting_point = data.starting_point;
                    lock_info.ending_point = data.ending_point;
                    lock_info.secret = data.lock_secret;
                    lock_info.type = 'snippet';
                    $current_inline_editor_div = $('div#' + anchor);
                    $current_inline_editor_div.find('.transcript').hide();
                    var $container = $current_inline_editor_div
                        .find('.inline-editor-container')
                        .show()
                    ;
                    $('#inline-editor-template')
                        .clone()
                        .appendTo($container)
                        .show()
                        .find('.inline-editor')
                        .focus()
                        .val(data.snippet_text)
                    ;
                    $('.play').addClass('hidden-while-editing');
                    $('.edit').addClass('hidden-while-editing');
                    $('#speakers').removeClass('hidden-while-viewing');
                    editor_replay();
                } else {
                    alert(data.message);
                }
            },
            // return data type
            'json'
        );
    }
  return false;
};


var inline_editor_save = function () {
    player_pause(true);
    if (has_identity(true)) {
        var data = {
            lock_secret: lock_info.secret,
            starting_point: lock_info.starting_point,
            snippet_text: $current_inline_editor_div.find('.inline-editor').val(),
            identity_name: $.cookie('identity_name'),
            identity_email: $.cookie('identity_email'),
            inline: 1
        };
        var url = '/save_snippet';
        $.post(url, data, function (data) {
            lock_info.secret = undefined;
            lock_info.starting_point = undefined;
            lock_info.ending_point = undefined;
            lock_info.type = undefined;
            // cleanup
            $current_inline_editor_div.find('.inline-editor-container').empty().hide();
            $current_inline_editor_div = undefined;
            $('.play').removeClass('hidden-while-editing');
            $('.edit').removeClass('hidden-while-editing');
            $('#speakers').addClass('hidden-while-viewing');
            // update this and any other snippets, and restart update schedule
            request_and_update_snippets();
            start_updating_snippets();
        });
    }
  return false;
};


var inline_editor_cancel = function () {
    player_pause(true);
    if (has_identity(true)) {
        var data = {
            lock_secret: lock_info.secret,
            starting_point: lock_info.starting_point,
            identity_name: $.cookie('identity_name'),
            identity_email: $.cookie('identity_email')
        };
        var url = '/cancel_snippet';
        $.post(url, data, function () {
            lock_info.secret = undefined;
            lock_info.starting_point = undefined;
            lock_info.ending_point = undefined;
            lock_info.type = undefined;
            $current_inline_editor_div.find('.inline-editor-container').empty().hide();
            $current_inline_editor_div.find('.transcript').show();
            $current_inline_editor_div = undefined;
            $('.play').removeClass('hidden-while-editing');
            $('.edit').removeClass('hidden-while-editing');
            $('#speakers').addClass('hidden-while-viewing');
            // update any other snippets edited, and restart update schedule
            request_and_update_snippets();
            start_updating_snippets();
        });
    }
  return false;
};


// =========================================================================
// player


// return the mp3 player flash object
var player = function () {
    return $('#player')[0];
};


// updated at intervals by the player
var player_listener = {
    enabled: false, // set to true by player_startup
    onInit: function () {
        this.position = 0;
    },
    onUpdate: function () {
        this.duration_difference = parseFloat(this.duration) - parseFloat(this.old_duration);
        this.old_duration = this.duration;
        if (this.duration_difference !== 0 && this.finished_timeout_id) {
            window.clearTimeout(this.finished_timeout_id);
        }
      this.update_player_info();
    },
    update_player_info: function () {
        $('#player-enabled').text(this.enabled);
        $('#player-isPlaying').text(this.isPlaying);
        $('#player-url').text(this.url);
        $('#player-volume').text(this.volume);
        $('#player-position').text(this.position === 'undefined' ? '--' : ms_to_label(parseFloat(this.position)));
        $('#player-duration').text(this.duration === 'undefined' ? '--' : ms_to_label(parseFloat(this.duration)));
        $('#player-bytesLoaded').text(this.bytesLoaded === 'undefined' ? '--' : parseFloat(this.bytesLoaded));
        $('#player-bytesTotal').text(this.bytesTotal === 'undefined' ? '--' : parseFloat(this.bytesTotal));
    }
};


// enable the mp3 player
var player_enable = function () {
    if (!(player().SetVariable)) {
        // On Firefox, the SetVariable function isn't available right away.
        window.setTimeout(player_enable, 100);
    } else if (!player_listener.volume) {
        player().SetVariable('enabled', 'true');
        // sometimes this is not immediate due to flash startup.
        // keep trying until the player is enabled.
        window.setTimeout(player_enable, 100);
    } else {
        // player was enabled and is updating the listener.
        player_listener.enabled = true;
        $('.needs-player').removeClass('no-player');
        $('.needs-unset-player').addClass('no-unset-player');
        player_setup_url();
    }
};


var player_shortcuts_enable = function () {
    $('body').keypress(function (event) {
        if (event.which == 96) { // `
            event.preventDefault();
            editor_rewind();
        } else if (event.which == 126) { // ~
            event.preventDefault();
            editor_replay(true);
        } else if (event.which == 92) { // \
            event.preventDefault();
            editor_pause_play();
        }
    });
};


// setup the mp3 player with the audio url
var player_setup_url = function () {
    player().SetVariable('method:stop', '');
    if (player_listener.enabled && transcription.audio_url) {
        player_listener.position = 'undefined';
        player().SetVariable('method:setUrl', transcription.audio_url);
        streaming_snippet = false;
    } else {
        // player not enabled or haven't received audio URL.
        // keep trying.
        window.setTimeout(player_setup_url, 100);
    }
};


// begin streaming (but do not play)
var player_begin_streaming = function () {
    player_play();
    player_pause(true);
};


var player_play = function () {
    player().SetVariable('method:play', '');
};


// set by player_play_from, and cancelled by player_pause
var wait_for_start_timeout;


var player_play_from_snippet_start = function () {
    var $snippetDiv = $(this).parents('.snippet');
    var snippetId = $snippetDiv.attr('id');
    var time_re = /(\d+)m(\d+)s/;
    var matches = snippetId.match(time_re);
    var minutes = parseFloat(matches[1]);
    var seconds = parseFloat(matches[2]);
    var starting_point = (minutes * 60 + seconds) * 1000;
    // wait until we have streamed past the start.
    var wait_for_start = function () {
        if (player_listener.duration === 'undefined' || parseFloat(player_listener.duration) < starting_point) {
            wait_for_start_timeout = window.setTimeout(wait_for_start, 500);
        } else {
            start_reached();
        }
    };
    // start playing, then stop at the end, when we have enough streamed.
    var start_reached = function () {
        player_seek(starting_point);
        player_play();
    };
    // now trigger the above functions appropriately.
    if (streaming_snippet) {
        // set up URL to use full audio, not a snippet
        player_setup_url();
        // wait to begin streaming to allow time for player to initialize with new URL.
        window.setTimeout(player_begin_streaming, 500);
        window.setTimeout(wait_for_start, 1000);
    } else if (player_listener.position == 'undefined') {
        player_begin_streaming();
        wait_for_start();
    } else {
        player_seek(starting_point);
    }
    return false;
};


// set by player_replay_at, cancelled by player_pause
var replay_timeout;
var position_check_timeout;


var player_pause = function (clear_timeouts) {
    if (position_check_timeout && clear_timeouts) {
        window.clearTimeout(position_check_timeout);
        position_check_timeout = undefined;
    }
  if (replay_timeout && clear_timeouts) {
        window.clearTimeout(replay_timeout);
        replay_timeout = undefined;
    }
  if (wait_for_start_timeout && clear_timeouts) {
        window.clearTimeout(wait_for_start_timeout);
        wait_for_start_timeout = undefined;
    }
  if (wait_for_end_timeout && clear_timeouts) {
        window.clearTimeout(wait_for_end_timeout);
        wait_for_end_timeout = undefined;
    }
  player().SetVariable('method:pause', '');
};


var player_replay_at_end = function () {
    if (position_check_timeout) {
        window.clearTimeout(position_check_timeout);
    }
  var position_check = function () {
        var duration = player_listener.duration === 'undefined' ? undefined : parseFloat(player_listener.duration);
        var position = player_listener.position === 'undefined' ? undefined : parseFloat(player_listener.position);
        if (position >= duration || (player_listener.isPlaying == 'false' && position == 0)) {
            // done playing; replay from beginning after one second.
            var replay = function () {
                player_play();
                player_replay_at_end();
            };
            replay_timeout = window.setTimeout(replay, 1000);
        } else {
            // haven't started playing, or still playing
            position_check_timeout = window.setTimeout(position_check, 500);
        }
    };
    // wait a while to start first position check, to allow player listener to be populated.
    position_check_timeout = window.setTimeout(position_check, 2500);
};


var player_seek = function (position) {
    player().SetVariable('method:setPosition', position);
};


// =========================================================================
// player preferences


var set_default_player_preferences = function () {
    if ($.cookie('auto_play_edit') === null) {
        $.cookie('auto_play_edit', '1', cookie_options);
    }
};


var fill_player_preferences = function () {
    if ($.cookie('auto_play_edit')) {
        $('#player-auto-play-edit').attr('checked', 'checked');
    } else {
        $('#player-auto-play-edit').removeAttr('checked');
    }
};


var player_auto_play_edit_changed = function () {
    $.cookie('auto_play_edit', $(this).attr('checked') ? '1' : '', cookie_options);
};


// =========================================================================
// server


var request_and_fill_speakers = function () {
    $.get(
        // url
        '/speakers.txt',
        // success
        function (data) {
            $('#speakers-text')
                .text(data)
            ;
        }
    );
};


var request_and_fill_progress = function () {
    $.getJSON(
        // url
        '/progress' + (url_params.rev ? '?rev=' + url_params.rev : ''),
        // success
        function (data) {
            $('#snippets-progress-percent')
                .find('span')
                    .css('width', data.snippets_progress.percent + '%')
                    .find('strong')
                        .text(data.snippets_progress.percent + '%')
            ;
            $('#snippets-progress-completed').text(data.snippets_progress.completed);
            $('#snippets-progress-total').text(data.snippets_progress.total);
            $('#reviews-progress-percent')
                .find('span')
                    .css('width', data.reviews_progress.percent + '%')
                    .find('strong')
                        .text(data.reviews_progress.percent + '%')
            ;
            $('#reviews-progress-completed').text(data.reviews_progress.completed);
            $('#reviews-progress-total').text(data.reviews_progress.total);
        }
    );
};


var request_and_update_snippets = function () {
    $.getJSON(
        // url
        '/updated?since=' + latest_revision + (url_params.rev ? '&rev=' + url_params.rev : ''),
        // success
        function (data) {
            // update latest revision to what server gave.
            latest_revision = data.latest_revision;
            if (data.snippets.length > 0) {
                request_and_fill_progress();
            }
            $.each(data.snippets, function (index, value) {
                // find the snippet corresponding to the starting point.
                var $snippet_div = $('div#' + ms_to_label(value.starting_point));
                // find the transcript inside it.
                var $old_transcript = $snippet_div.find('.transcript');
                var $new_transcript = $('<dl class="transcript"></dl>');
                // build the new transcript line by line.
                var last_abbreviation = '';
                $.each(value.lines, function (index2, value2) {
                    var abbreviation = value2[0];
                    var speaker = value2[1];
                    var spoken = value2[2];
                    if (abbreviation && abbreviation != last_abbreviation) {
                        last_abbreviation = abbreviation;
                        $new_transcript
                            .append(
                                $('<dt>:</dt>')
                                    .prepend(
                                        $('<span class="name"/>')
                                            .text(speaker)
                                    )
                                    .addClass('speaker-' + abbreviation)
                            )
                        ;
                    }
                    $new_transcript.append(
                        $('<dd/>')
                            .addClass('speaker-' + last_abbreviation)
                            .text(spoken)
                    );
                });
                $old_transcript.replaceWith($new_transcript);
            });
        }
    );
};


var update_snippets_timeout;


var start_updating_snippets = function () {

    // temporarily disable until we can figure out memory leak issue
    return undefined;

    var schedule_next_update = function () {
        update_snippets_timeout = window.setTimeout(do_update, UPDATE_SNIPPETS_INTERVAL);
    };
    var do_update = function () {
        request_and_update_snippets();
        schedule_next_update();
    };
    schedule_next_update();
};


var stop_updating_snippets = function () {
    window.clearTimeout(update_snippets_timeout);
    update_snippets_timeout = undefined;
};



// =========================================================================
// contribution info & other metadata


var show_snippet_info = function (anchor, starting_point) {
    $.getJSON(
        // url
        '/snippet_info' + (url_params.rev ? '?rev=' + url_params.rev : ''),
        // data
        {
            starting_point: starting_point
        },
        // success
        function (data) {
            var $container = $('div#' + anchor).find('div.snippet-info-container');
            var $snippet_info = $('#snippet-info-template')
                .clone()
                .appendTo($container.empty())
                .show()
            ;
            var $contributor_list = $snippet_info.find('ul.contributor-list');
            if (data.contributor_list.length > 0) {
                $.each(data.contributor_list, function (index, value) {
                    $('<li/>')
                        .appendTo($contributor_list)
                        .text(value.author_name)
                    ;
                });
            } else {
                $('<li>(No contributors found)</li>').appendTo($contributor_list);
            }
        }
    );
};


// =========================================================================
// browser url
// http://stackoverflow.com/a/2880929/72560


var url_params = {};
(function () {
    var e,
        a = /\+/g,  // Regex for replacing addition symbol with a space
        r = /([^&=]+)=?([^&]*)/g,
        d = function (s) { return decodeURIComponent(s.replace(a, " ")); },
        q = window.location.search.substring(1);

    while (e = r.exec(q))
       url_params[d(e[1])] = d(e[2]);
})();


// =========================================================================
// helpers

// http://stackoverflow.com/questions/1267283/how-can-i-create-a-zerofilled-value-using-javascript
var zeroFill = function(number, width)
{
  width -= number.toString().length;
  if ( width > 0 )
  {
    return new Array( width + (/\./.test( number ) ? 2 : 1) ).join( '0' ) + number;
  }
  return number;
};

var ms_to_label = function (ms) {
    var seconds = ms / 1000;
    var minutes = Math.floor(seconds / 60);
    seconds = Math.floor(seconds % 60);
    return (minutes + 'm' + zeroFill(seconds, 2) + 's');
};
