// onload


var edit_onload = function () {
    fill_identity();
    request_and_fill_about();
    request_and_fill_speakers();
};


var view_onload = function () {
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


// info requests


var request_and_fill_about = function () {
    $.getJSON(
        // url
        '/transcription.json',
        // success
        function (data) {
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
