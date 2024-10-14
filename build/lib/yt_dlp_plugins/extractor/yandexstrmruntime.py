from yt_dlp.extractor.common import InfoExtractor
from yt_dlp.utils import (
    determine_ext,
    int_or_none,
    url_or_none,
)


class YandexSTRMRuntimeIE(InfoExtractor):
    _VALID_URL = r'''(?x)
                    https?://runtime\.strm\.yandex\.ru/player/
                        (?P<id>([\w/-]+))
                    '''

    def _real_extract(self, url):
        video_id = self._match_id(url)

        player = self._download_json(
            f'https://runtime.strm.yandex.ru/player/{video_id}.json',
            video_id, query={
                'stream_options': 'hires',
                'disable_trackings': 1,
            })
        content = player['content']

        title = content.get('title') or content['computed_title']

        formats = []
        streams = content.get('streams') or []
        streams.append({'url': content.get('content_url')})
        for stream in streams:
            content_url = url_or_none(stream.get('url'))
            if not content_url:
                continue
            ext = determine_ext(content_url)
            if ext == 'ismc':
                continue
            elif ext == 'm3u8':
                formats.extend(self._extract_m3u8_formats(
                    content_url, video_id, 'mp4',
                    'm3u8_native', m3u8_id='hls', fatal=False))
            elif ext == 'mpd':
                formats.extend(self._extract_mpd_formats(
                    content_url, video_id, mpd_id='dash', fatal=False))
            else:
                formats.append({'url': content_url})

        timestamp = (int_or_none(content.get('release_date'))
                     or int_or_none(content.get('release_date_ut'))
                     or int_or_none(content.get('start_time')))
        season = content.get('season') or {}

        return {
            'id': video_id,
            'title': title,
            'description': content.get('description'),
            'thumbnail': content.get('thumbnail'),
            'timestamp': timestamp,
            'duration': int_or_none(content.get('duration')),
            'series': content.get('program_title'),
            'age_limit': int_or_none(content.get('restriction_age')),
            'view_count': int_or_none(content.get('views_count')),
            'like_count': int_or_none(content.get('likes')),
            'dislike_count': int_or_none(content.get('dislikes')),
            'season_number': int_or_none(season.get('season_number')),
            'season_id': season.get('id'),
            'release_year': int_or_none(content.get('release_year')),
            'formats': formats,
        }