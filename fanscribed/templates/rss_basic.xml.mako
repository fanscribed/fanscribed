<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
    <channel>
        <title>Activity feed for ${transcription_info['title']} transcript at http://${request.host}/</title>
        <link>http://${request.host}/</link>
        <lastBuildDate>${rfc822_from_time(pub_date)}</lastBuildDate>
        <pubDate>${rfc822_from_time(pub_date)}</pubDate>
        <ttl>60</ttl>
        <generator>Fanscribed</generator>
        % for action in actions:
            <item>
                <title>Contribution by ${action['author'].name} at ${action['position']}</title>
                <link>${action['now_url']}</link>
                <description>
                    ${action['author'].name} contributed to position ${action['position']}
                    in the "${transcription_info['title']}" transcript at http://${request.host}/.

                    Text at this position, now: ${action['now_url']}.
                    Text at this position, at time of contribution: ${action['this_url']}.
                </description>
                <pubDate>${rfc822_from_time(action['date'])}</pubDate>
                <guid>${action['this_url']}</guid>
            </item>
        % endfor
    </channel>
</rss>
