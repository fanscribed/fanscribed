// onload


var edit_onload = function () {
    player_enable();
    fill_identity();
    request_and_fill_about();
    request_and_fill_speakers();
};


var view_onload = function () {
    player_enable();
    request_and_fill_about();
    request_and_fill_speakers();
};


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
    } else {
        // player not enabled or haven't received audio URL.
        // keep trying.
        window.setTimeout(player_setup_url, 100);
    }
};


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
