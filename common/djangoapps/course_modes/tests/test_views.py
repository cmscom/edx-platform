import ddt
import unittest
from django.test import TestCase
from django.conf import settings
from django.core.urlresolvers import reverse
from mock import patch, Mock

from course_modes.tests.factories import CourseModeFactory
from student.tests.factories import CourseEnrollmentFactory, UserFactory
from opaque_keys.edx.locations import SlashSeparatedCourseKey


@ddt.ddt
class CourseModeViewTest(TestCase):

    def setUp(self):
        self.course_id = SlashSeparatedCourseKey('org', 'course', 'run')

        for mode in ('audit', 'verified', 'honor'):
            CourseModeFactory(mode_slug=mode, course_id=self.course_id)

    @unittest.skipUnless(settings.ROOT_URLCONF == 'lms.urls', 'Test only valid in lms')
    @ddt.data(
        # is_active?, enrollment_mode, upgrade?, redirect? auto_register?
        (True, 'verified', True, True, False),     # User is already verified
        (True, 'verified', False, True, False),    # User is already verified
        (True, 'honor', True, False, False),       # User isn't trying to upgrade
        (True, 'honor', False, True, False),       # User is trying to upgrade
        (True, 'audit', True, False, False),       # User isn't trying to upgrade
        (True, 'audit', False, True, False),       # User is trying to upgrade
        (False, 'verified', True, False, False),   # User isn't active
        (False, 'verified', False, False, False),  # User isn't active
        (False, 'honor', True, False, False),      # User isn't active
        (False, 'honor', False, False, False),     # User isn't active
        (False, 'audit', True, False, False),      # User isn't active
        (False, 'audit', False, False, False),     # User isn't active

        # When auto-registration is enabled, users may already be
        # registered when they reach the "choose your track"
        # page.  In this case, we do NOT want to redirect them
        # to the dashboard, because we want to give them the option
        # to enter the verification/payment track.
        # TODO: based on the outcome of the auto-registration AB test,
        # either keep these tests or remove them.  In either case,
        # remove the "auto_register" flag from this test case.
        (True, 'verified', True, False, True),
        (True, 'verified', False, False, True),
        (True, 'honor', True, False, True),
        (True, 'honor', False, False, True),
        (True, 'audit', True, False, True),
        (True, 'audit', False, False, True),
    )
    @ddt.unpack
    @patch('course_modes.views.modulestore', Mock())
    def test_reregister_redirect(self, is_active, enrollment_mode, upgrade, redirect, auto_register):
        enrollment = CourseEnrollmentFactory(
            is_active=is_active,
            mode=enrollment_mode,
            course_id=self.course_id
        )

        self.client.login(
            username=enrollment.user.username,
            password='test'
        )

        if upgrade:
            get_params = {'upgrade': True}
        else:
            get_params = {}

        url_name = (
            'course_modes_choose'
            if not auto_register
            else 'course_modes_choose_autoreg'
        )
        url = reverse(url_name, args=[self.course_id.to_deprecated_string()])
        response = self.client.get(url, get_params)

        if redirect:
            self.assertRedirects(response, reverse('dashboard'))
        else:
            self.assertEquals(response.status_code, 200)
            # TODO: Fix it so that response.templates works w/ mako templates, and then assert
            # that the right template rendered

    @unittest.skipUnless(settings.ROOT_URLCONF == 'lms.urls', 'Test only valid in lms')
    @ddt.data(
        '',
        '1,,2',
        '1, ,2',
        '1, 2, 3'
    )
    @patch('course_modes.views.modulestore', Mock())
    def test_suggested_prices(self, price_list):
        course_id = SlashSeparatedCourseKey('org', 'course', 'price_course')
        user = UserFactory()

        for mode in ('audit', 'honor'):
            CourseModeFactory(mode_slug=mode, course_id=course_id)

        CourseModeFactory(mode_slug='verified', course_id=course_id, suggested_prices=price_list)

        self.client.login(
            username=user.username,
            password='test'
        )

        response = self.client.get(
            reverse('course_modes_choose', args=[self.course_id.to_deprecated_string()]),
            follow=False,
        )

        self.assertEquals(response.status_code, 200)
        # TODO: Fix it so that response.templates works w/ mako templates, and then assert
        # that the right template rendered


class ProfessionalModeViewTest(TestCase):
    """
    Tests for redirects specific to the 'professional' course mode.
    Can't really put this in the ddt-style tests in CourseModeViewTest,
    since 'professional' mode implies it is the *only* mode for a course
    """
    def setUp(self):
        self.course_id = SlashSeparatedCourseKey('org', 'course', 'run')
        CourseModeFactory(mode_slug='professional', course_id=self.course_id)
        self.user = UserFactory()

    @unittest.skipUnless(settings.ROOT_URLCONF == 'lms.urls', 'Test only valid in lms')
    def test_professional_registration(self):
        self.client.login(
            username=self.user.username,
            password='test'
        )

        response = self.client.get(
            reverse('course_modes_choose', args=[self.course_id.to_deprecated_string()]),
            follow=False,
        )

        self.assertEquals(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(reverse('verify_student_show_requirements', args=[unicode(self.course_id)])))

        CourseEnrollmentFactory(
            user=self.user,
            is_active=True,
            mode="professional",
            course_id=unicode(self.course_id),
        )

        response = self.client.get(
            reverse('course_modes_choose', args=[self.course_id.to_deprecated_string()]),
            follow=False,
        )

        self.assertEquals(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(reverse('dashboard')))
