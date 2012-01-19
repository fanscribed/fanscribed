// =========================================================================
// onload


var duration_sent = false;
var should_auto_stream = false;


var edit_onload = function () {
    if (url_params.autostream === '0') {
        // url requested no auto streaming.
        should_auto_stream = false;
    } else {
        // default: automatically start streaming
        should_auto_stream = true;
    };
    player_enable();
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
    var name = $.cookie('identity-name');
    var email = $.cookie('identity-email');
    $('#identity-name').val(name);
    $('#identity-email').val(email);
};


var save_identity = function () {
    var name = $('#identity-name').val();
    var email = $('#identity-email').val();
    $.cookie('identity-name', name, cookieOptions);
    $.cookie('identity-email', email, cookieOptions);
    $('#identity-saved').text('Saved!');
    var clear = function () { $('#identity-saved').text(''); };
    window.setTimeout(clear, 1000);
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
    if (!player_listener.volume) {
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
    player_pause();
};


var player_play = function () {
    player().SetVariable('method:play', '');
};
var player_pause = function () {
    player().SetVariable('method:pause', '');
};


// =========================================================================
// server


var transcription = {};


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
        $.post(
            // url
            '/save_duration',
            // data
            {
                duration: player_listener.duration,
                bytes_total: player_listener.bytesTotal,
                init_password: url_params.init
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
