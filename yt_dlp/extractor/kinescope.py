from .common import InfoExtractor
from ..utils import (
    float_or_none,
    int_or_none,
    js_to_json,
    traverse_obj,
    unified_timestamp,
)


class KinescopeIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?kinescope\.io/(?:embed/)?(?P<id>[\w-]+)'
    _EMBED_REGEX = [r'<iframe[^>]+src=["\'](?P<url>https?://(?:www\.)?kinescope\.io/embed/[\w-]+)']
    _TESTS = [{
        'url': 'https://kinescope.io/mJMGKQBudWgcHucMYoQd3g',
        'info_dict': {
            'id': 'a7f02d44-2779-4d05-8197-638ee7d816d3',
            'ext': 'mp4',
            'title': 'video_2025-10-16_19-40-33',
            'thumbnail': r're:https?://.*\.jpg$',
            'duration': 16.667,
            'width': 720,
            'height': 1280,
            'description': 'md5:312c5e606934c87a1814097852778e01',
            'timestamp': 1761643617,
            'upload_date': '20251028',
        },
    }, {
        'url': 'https://kinescope.io/embed/a7f02d44-2779-4d05-8197-638ee7d816d3',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        display_id = self._match_id(url)
        webpage = self._download_webpage(url, display_id)

        player_data = self._search_json(
            r'var\s+playerOptions\s*=', webpage, 'player data', display_id,
            transform_source=js_to_json)

        video_info = player_data['playlist'][0]
        video_id = video_info['id']

        formats = []
        sources = video_info.get('sources', {})

        hls_url = traverse_obj(sources, ('hls', 'src'))
        if hls_url:
            formats.extend(self._extract_m3u8_formats(
                hls_url, video_id, 'mp4', m3u8_id='hls', fatal=False))

        shakahls_url = sources.get('shakahls')
        if shakahls_url and shakahls_url != hls_url:
            formats.extend(self._extract_m3u8_formats(
                shakahls_url, video_id, 'mp4', m3u8_id='shakahls', fatal=False))

        thumbnail = traverse_obj(video_info, (
            'poster', 'src', 'src')) or video_info.get('posterInPreview')

        meta = video_info.get('meta', {})

        return {
            'id': video_id,
            'title': video_info.get('title') or self._og_search_title(webpage, default=None),
            'description': video_info.get('description') or self._og_search_description(webpage, default=None),
            'thumbnail': thumbnail,
            'duration': float_or_none(meta.get('duration')),
            'width': int_or_none(self._og_search_property('video:width', webpage, default=None)),
            'height': int_or_none(self._og_search_property('video:height', webpage, default=None)),
            'timestamp': unified_timestamp(self._og_search_property('video:release_date', webpage, default=None)),
            'formats': formats,
        }
