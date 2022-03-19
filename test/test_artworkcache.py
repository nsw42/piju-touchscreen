import unittest
from unittest.mock import patch, call

from apiclient import ApiClient, ArtworkInfo
from artworkcache import ArtworkCache


class TestUpdate(unittest.TestCase):
    @patch.object(ApiClient, 'get_artwork_info')
    def test_update_none_to_none(self, mock_get_artwork_info):
        apiclient = ApiClient('http://address/')
        cache = ArtworkCache()
        cache.update(apiclient, None)
        mock_get_artwork_info.assert_not_called()

    @patch.object(ApiClient, 'get_artwork',
                  return_value='SomeArtworkHere')
    @patch.object(ApiClient, 'get_artwork_info',
                  return_value=ArtworkInfo(width=27, height=36, imageuri='/artwork/123'))
    def test_update_none_to_uri(self, mock_get_artwork_info, mock_get_artwork):
        apiclient = ApiClient('http://address/')
        cache = ArtworkCache()
        cache.update(apiclient, '/artwork_info/123')
        mock_get_artwork_info.assert_called_once_with('/artwork_info/123')
        mock_get_artwork.assert_called_once_with('/artwork/123')

    @patch.object(ApiClient, 'get_artwork_info',
                  return_value=ArtworkInfo(width=27, height=36, imageuri='/artwork/123'))
    def test_update_uri_to_none(self, mock_get_artwork_info):
        apiclient = ApiClient('http://address/')
        cache = ArtworkCache()
        # set up the initial state:
        cache.update(apiclient, '/artwork_info/123')
        mock_get_artwork_info.assert_called_once_with('/artwork_info/123')
        # now call again with uri=None:
        cache.update(apiclient, None)
        mock_get_artwork_info.assert_called_once()

    @patch.object(ApiClient, 'get_artwork_info',
                  return_value=ArtworkInfo(width=27, height=36, imageuri='/artwork/123'))
    def test_update_uri_to_same_uri(self, mock_get_artwork_info):
        apiclient = ApiClient('http://address/')
        cache = ArtworkCache()
        info_uri = '/artwork_info/456'
        # set up the initial state:
        cache.update(apiclient, info_uri)
        mock_get_artwork_info.assert_called_once_with(info_uri)
        # now call again with same parameters:
        cache.update(apiclient, info_uri)
        mock_get_artwork_info.assert_called_once_with(info_uri)

    @patch.object(ApiClient, 'get_artwork_info',
                  return_value=ArtworkInfo(width=27, height=36, imageuri='/artwork/123'))
    def test_update_uri_to_different_uri(self, mock_get_artwork_info):
        apiclient = ApiClient('http://address/')
        cache = ArtworkCache()
        info_uri_1 = '/artwork_info/123'
        info_uri_2 = '/artwork_info/456'
        # set up the initial state:
        cache.update(apiclient, info_uri_1)
        expected_calls = [call(info_uri_1)]
        mock_get_artwork_info.assert_has_calls(expected_calls)
        # now call again with different parameters:
        cache.update(apiclient, info_uri_2)
        expected_calls.append(call(info_uri_2))
        mock_get_artwork_info.assert_has_calls(expected_calls)

    @patch.object(ApiClient, 'get_artwork')
    @patch.object(ApiClient, 'get_artwork_info', side_effect=[
        ArtworkInfo(width=27, height=36, imageuri='/artwork/999'),
        ArtworkInfo(width=54, height=72, imageuri=None)
    ])
    def test_update_for_new_image_does_not_get_null_artwork(self, mock_get_artwork_info, mock_get_artwork):
        apiclient = ApiClient('http://address/')
        cache = ArtworkCache()
        cache.update(apiclient, '/artwork_info/999')
        mock_get_artwork_info.assert_called_once_with('/artwork_info/999')
        mock_get_artwork.assert_called_once_with('/artwork/999')

        cache.update(apiclient, '/artwork_info/998')
        mock_get_artwork_info.has_calls([call('/artwork_info/999'), call('/artwork_info/998')])
        mock_get_artwork.assert_called_once_with('/artwork/999')
