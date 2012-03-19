<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
    <channel>
        <title>Kudos for ${transcription_info['title']} transcript at http://${request.host}/</title>
        <link>http://${request.host}/</link>
        <lastBuildDate>${rfc822_from_time(pub_date)}</lastBuildDate>
        <pubDate>${rfc822_from_time(pub_date)}</pubDate>
        <ttl>60</ttl>
        <generator>Fanscribed</generator>
        % for timegroup, authors in timegroup_author_actions.iteritems():
            % for author_name, author_info in authors.iteritems():
                <%
                latest_action = author_info['latest_action']
                %>
                <item>
                    <title>Kudos for ${author_name}</title>
                    <link>${latest_action['now_url']}</link>
                    <description>${author_info['kudos']}</description>
                    <pubDate>${rfc822_from_time(latest_action['date'])}</pubDate>
                    <guid>${latest_action['this_url']}</guid>
                </item>
            % endfor
        % endfor
    </channel>
</rss>
