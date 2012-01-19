// onload


var edit_onload = function () {
    request_and_fill_about();
    request_and_fill_speakers();
};


var view_onload = function () {
    request_and_fill_about();
    request_and_fill_speakers();
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
