// =========================================================================
// constants


var PADDING = 2500; // 2.5 second audio padding on either side of a snippet


// =========================================================================
// globals (yes, I know... run away screaming!)


var duration_sent = false;
var should_auto_stream = false;
var transcription = {};


// =========================================================================
// onload


var edit_onload = function () {
    if (url_params.autostream === '0') {
        // url requested no auto streaming.
        should_auto_stream = false;
    } else {
        // default: automatically start streaming
        should_auto_stream = true;
    };
    player_enable();
    player_shortcuts_enable();
    fill_identity();
    request_and_fill_about();
    request_and_fill_speakers();
};


var view_onload = function () {
    if (url_params.autostream === '1') {
        // url requested auto streaming.
        should_auto_stream = true;
    } else {
        // default: do not automatically start streaming
        should_auto_stream = false;
    };
    player_enable();
    request_and_fill_about();
    request_and_fill_speakers();
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
    $.cookie('identity_name', name, cookieOptions);
    $.cookie('identity_email', email, cookieOptions);
    $('#identity-saved').text('Saved!');
    var clear = function () { $('#identity-saved').text(''); };
    window.setTimeout(clear, 1000);
    return false;
};


var has_identity = function () {
    if (!($.cookie('identity_name')) || !($.cookie('identity_email'))) {
        alert('Must set identity before continuing.');
        return false;
    } else {
        return true;
    };
};


// =========================================================================
// editor


var lock_info = {
    starting_point: undefined,
    ending_point: undefined,
    secret: undefined,
    type: undefined
};


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
    if (has_identity()) {
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
    };
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


var editor_transcribe = function () {
    if (has_identity()) {
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
                    editor_replay();
                } else {
                    alert(data.message);
                };
            },
            // return data type
            'json'
        );
    };
    return false;
};


var editor_review = function () {
    if (has_identity()) {
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
                    editor_replay();
                } else {
                    alert(data.message);
                };
            },
            // return data type
            'json'
        );
    };
    return false;
};


var editor_save = function () {
    player_pause(true);
    if (has_identity()) {
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
        };
        $.post(url, data, function (data) {
            lock_info.secret = undefined;
            lock_info.starting_point = undefined;
            lock_info.ending_point = undefined;
            lock_info.type = undefined;
            $('#edit-buttons').show();
            $('#edit-action-buttons').hide();
            $('#transcribe-editor').hide();
            $('#review-editor1').hide();
            $('#review-editor2').hide();
            $('#instructions-transcribe').hide();
            $('#instructions-review').hide();
        });
    };
    return false;
};


var editor_cancel = function () {
    player_pause(true);
    if (has_identity()) {
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
        };
        $.post(url, data, function (data) {
            lock_info.secret = undefined;
            lock_info.starting_point = undefined;
            lock_info.ending_point = undefined;
            lock_info.type = undefined;
            $('#edit-buttons').show();
            $('#edit-action-buttons').hide();
            $('#transcribe-editor').hide();
            $('#review-editor1').hide();
            $('#review-editor2').hide();
            $('#instructions-transcribe').hide();
            $('#instructions-review').hide();
        });
    };
    return false;
};


var editor_replay = function () {
    var actual_start = lock_info.starting_point - PADDING;
    var actual_end = lock_info.ending_point + PADDING;
    if (actual_start < 0) {
        actual_start = 0;
    };
    if (actual_end > transcription.duration) {
        actual_end = transcription.duration;
    };
    player_pause(true);
    // wait until we have streamed past the end.
    var wait_for_end = function () {
        if (parseFloat(player_listener.duration) < actual_end) {
            window.setTimeout(wait_for_end, 500);
        } else {
            end_reached();
        };
    };
    // start playing, then stop at the end, when we have enough streamed.
    var end_reached = function () {
        player_seek(actual_start);
        player_play();
        player_replay_at(actual_end, editor_replay);
    };
    wait_for_end();
    return false;
};


var editor_pause_play = function () {
    if (player_listener.isPlaying == 'true') {
        player_pause(false);
    } else {
        // seek backward 500 ms to prevent skipping over audio
        var actual_start = lock_info.starting_point - PADDING;
        if (actual_start < 0) {
            actual_start = 0;
        };
        var new_position = player_listener.position - 500;
        if (new_position < actual_start) {
            // don't go past beginning of snippet.
            new_position = actual_start;
        };
        player_seek(new_position);
        player_play();
    };
};


var editor_rewind = function () {
    var actual_start = lock_info.starting_point - PADDING;
    if (actual_start < 0) {
        actual_start = 0;
    };
    var new_position = player_listener.position - 5000;
    if (new_position < actual_start) {
        // don't go past beginning of snippet.
        new_position = actual_start;
    };
    player_seek(new_position);
    if (player_listener.isPlaying != 'true') {
        player_play();
    };
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
        };
        this.update_player_info();
        this.send_duration_if_finished();
    },
    send_duration_if_finished: function () {
        if (this.bytesLoaded !== 'undefined' && (this.bytesLoaded == this.bytesTotal) && (this.duration_difference === 0) && (!this.finished_timeout_id)) {
            // Wait five seconds before sending.
            // (File may be done loading, but player still processing duration)
            this.finished_timeout_id = window.setTimeout(send_duration, 5000);
        }
    },
    update_player_info: function () {
        $('#player-enabled').text(this.enabled);
        $('#player-isPlaying').text(this.isPlaying);
        $('#player-url').text(this.url);
        $('#player-volume').text(this.volume);
        $('#player-position').text(this.position);
        $('#player-position-minutes').text(this.position / 60000);
        $('#player-duration').text(this.duration);
        $('#player-duration-minutes').text(this.duration / 60000);
        $('#player-bytesLoaded').text(this.bytesLoaded);
        $('#player-bytesTotal').text(this.bytesTotal);
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
        player_setup_url();
    }
};


var player_shortcuts_enable = function () {
    $('.player-shortcuts').keypress(function (event) {
        if (event.which == 96) { // `
            event.preventDefault();
            editor_rewind();
        } else if (event.which == 126) { // ~
            event.preventDefault();
            editor_replay();
        } else if (event.which == 92) { // \
            event.preventDefault();
            editor_pause_play();
        };
    });
};


// setup the mp3 player with the audio url
var player_setup_url = function () {
    if (player_listener.enabled && transcription.audio_url) {
        player().SetVariable('method:setUrl', transcription.audio_url);
        if (should_auto_stream) {
            window.setTimeout(player_begin_streaming, 100);
        };
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


// used by player_pause and player_replay_at
var replay_timeout;
var position_check_timeout;


var player_pause = function (clear_timeouts) {
    if (position_check_timeout && clear_timeouts) {
        window.clearTimeout(position_check_timeout);
        position_check_timeout = undefined;
    };
    if (replay_timeout && clear_timeouts) {
        window.clearTimeout(replay_timeout);
        replay_timeout = undefined;
    };
    player().SetVariable('method:pause', '');
};


var player_replay_at = function (end_position, replay_function) {
    if (position_check_timeout) {
        window.clearTimeout(position_check_timeout);
    };
    var position_check = function () {
        if (parseFloat(player_listener.position) >= end_position) {
            player_pause(true);
            // wait one second, then replay.
            replay_timeout = window.setTimeout(replay_function, 1000);
        } else {
            position_check_timeout = window.setTimeout(position_check, 500);
        };
    };
    position_check();
};


var player_seek = function (position) {
    player().SetVariable('method:setPosition', position);
};


// =========================================================================
// server


var request_and_fill_about = function () {
    $.getJSON(
        // url
        '/transcription.json',
        // success
        function (data) {
            transcription = data;
            $('#about-title')
                .text(data.title)
            ;
            $('#about-homepage')
                .attr('href', data.homepage_url)
                .text(data.homepage_url)
            ;
            $('#about-audio')
                .attr('href', data.audio_url)
                .text(data.audio_url)
            ;
            $('#about-initialized')
                .text(data.duration ? "Yes" : "No")
            ;
        }
    );
};


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


// send duration and total bytes to server if ?init=<password> set in URL
var send_duration = function () {
    if (!duration_sent && url_params.init) {
        if (has_identity()) {
            $.post(
                // url
                '/save_duration',
                // data
                {
                    duration: player_listener.duration,
                    bytes_total: player_listener.bytesTotal,
                    init_password: url_params.init,
                    identity_name: $.cookie('identity_name'),
                    identity_email: $.cookie('identity_email')
                },
                // success
                function (data) {
                    alert('Initialization response: ' + data);
                }
            );
            // only send it once.
            duration_sent = true;
        };
    };
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