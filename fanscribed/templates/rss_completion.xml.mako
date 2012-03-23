<?xml version="1.0" encoding="UTF-8" ?>
<%
title = transcription_info['title']
%>
<rss version="2.0">
    <channel>
        <title>Completion history for ${title} transcript at http://${request.host}/</title>
        <link>http://${request.host}/</link>
        <lastBuildDate>${rfc822_from_time(pub_date)}</lastBuildDate>
        <pubDate>${rfc822_from_time(pub_date)}</pubDate>
        <ttl>60</ttl>
        <generator>Fanscribed</generator>
        % for percent_transcribed, percent_reviewed, this_url, date in completions:
            <item>
                <title>Completion progress</title>
                <link>${now_url}</link>
                % if percent_transcribed is not None:
                    <description>${now_url} now ${percent_transcribed}% transcribed: ${title}</description>
                % elif percent_reviewed is not None:
                    <description>${now_url} now ${percent_reviewed}% reviewed: ${title}</description>
                % endif
                <pubDate>${rfc822_from_time(date)}</pubDate>
                <guid>${this_url}</guid>
            </item>
        % endfor
    </channel>
</rss>
