# -*- coding: utf-8 -*-

"""
Acceptance tests for CMS Video Transcripts.

For transcripts acceptance tests there are 3 available caption
files. They can be used to test various transcripts features. Two of
them can be imported from YouTube.

The length of each file name is 11 characters. This is because the
YouTube's ID length is 11 characters. If file name is not of length 11,
front-end validation will not pass.

    t__eq_exist - this file exists on YouTube, and can be imported
                  via the transcripts menu; after import, this file will
                  be equal to the one stored locally
    t_neq_exist - same as above, except local file will differ from the
                  one stored on YouTube
    t_not_exist - this file does not exist on YouTube; it exists locally
"""

from .test_studio_video_module import CMSVideoBaseTest


class VideoTranscriptTest(CMSVideoBaseTest):
    """
    CMS Video Transcript Test Class
    """

    def setUp(self):
        super(VideoTranscriptTest, self).setUp()

    def test_input_validation(self):
        """
        Scenario: Check input error messages
        Given I have created a Video component
        And I edit the component

        #User inputs html5 links with equal extension
        And I enter a "123.webm" source to field number 1
        And I enter a "456.webm" source to field number 2
        Then I see error message "Link types should be unique."
        # Currently we are working with 2nd field. It means, that if 2nd field
        # contain incorrect value, 1st and 3rd fields should be disabled until
        # 2nd field will be filled by correct correct value
        And I expect 1 and 3 inputs are disabled
        When I clear fields
        And I expect inputs are enabled

        #User input URL with incorrect format
        And I enter a "http://link.c" source to field number 1
        Then I see error message "Incorrect url format."
        # Currently we are working with 1st field. It means, that if 1st field
        # contain incorrect value, 2nd and 3rd fields should be disabled until
        # 1st field will be filled by correct correct value
        And I expect 2 and 3 inputs are disabled

        #User input URL with incorrect format
        And I enter a "http://goo.gl/pxxZrg" source to field number 1
        And I enter a "http://goo.gl/pxxZrg" source to field number 2
        Then I see error message "Links should be unique."
        And I expect 1 and 3 inputs are disabled

        And I clear fields
        And I expect inputs are enabled

        And I enter a "http://youtu.be/t_not_exist" source to field number 1
        Then I do not see error message
        And I expect inputs are enabled
        """
        self.navigate_to_course_unit()

        from nose.tools import set_trace; set_trace()

        self.edit_component()

        self.video.set_url_field('123.webm', 1)

        self.video.set_url_field('456.webm', 2)

        self.assertEqual(self.video.field_status_message(), 'Link types should be unique.')

        self.assertEqual(self.video.url_field_status(1, 3).values(), [False, False])

        self.video.clear_fields()

        self.assertEqual(self.video.url_field_status().values(), [True, True, True])

        self.video.set_url_field('http://link.c', 1)

        self.assertEqual(self.video.field_status_message(), 'Incorrect url format.')

        self.assertEqual(self.video.url_field_status(2, 3).values(), [False, False])

        self.video.set_url_field('http://goo.gl/pxxZrg', 1)

        self.video.set_url_field('http://goo.gl/pxxZrg', 2)

        self.assertEqual(self.video.field_status_message(), 'Links should be unique.')

        self.assertEqual(self.video.url_field_status(1, 3).values(), [False, False])

        self.video.clear_fields()

        self.assertEqual(self.video.url_field_status().values(), [True, True, True])

        self.video.set_url_field('http://youtu.be/t_not_exist', 1)

        self.assertEqual(self.video.field_status_message(), '')

        self.assertEqual(self.video.url_field_status().values(), [True, True, True])
