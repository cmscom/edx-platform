from django.conf.urls import include, patterns, url
from django.conf import settings

from django.views.generic import TemplateView

from course_modes import views

urlpatterns = patterns(
    '',
    # pylint seems to dislike as_view() calls because it's a `classonlymethod` instead of `classmethod`, so we disable the warning
    url(r'^choose/{}/$'.format(settings.COURSE_ID_PATTERN), views.ChooseModeView.as_view(), name="course_modes_choose"),  # pylint: disable=no-value-for-parameter

    # This URL is used for an AB test of auto-registration.
    # TODO: Depending on the outcome of the AB test, update the original view and deprecate this URL.
    url(
        r'^choose_autoreg/{}/$'.format(settings.COURSE_ID_PATTERN),
        views.ChooseModeView.as_view(),
        {'auto_register': True},
        name="course_modes_choose_autoreg"
    ),
)
