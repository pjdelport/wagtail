from django.conf.urls import url, include
from django.contrib.auth.decorators import permission_required
from django.contrib.auth import views as django_auth_views
from django.views.decorators.cache import cache_control

from wagtail.wagtailadmin.forms import PasswordResetForm
from wagtail.wagtailadmin.views import account, chooser, home, pages, tags, userbar, page_privacy
from wagtail.wagtailcore import hooks
from wagtail.utils.urlpatterns import decorate_urlpatterns


urlpatterns = [
    url(r'^$', home.home, name='wagtailadmin_home'),

    url(r'^failwhale/$', home.error_test, name='wagtailadmin_error_test'),

    url(r'^explorer-nav/$', pages.explorer_nav, name='wagtailadmin_explorer_nav'),

    # TODO: Move into wagtailadmin_pages namespace
    url(r'^pages/$', pages.index, name='wagtailadmin_explore_root'),
    url(r'^pages/(\d+)/$', pages.index, name='wagtailadmin_explore'),

    url(r'^pages/', include([
        url(r'^new/(\w+)/(\w+)/(\d+)/$', pages.create, name='create'),
        url(r'^new/(\w+)/(\w+)/(\d+)/preview/$', pages.preview_on_create, name='preview_on_create'),
        url(r'^usage/(\w+)/(\w+)/$', pages.content_type_use, name='type_use'),

        url(r'^(\d+)/edit/$', pages.edit, name='edit'),
        url(r'^(\d+)/edit/preview/$', pages.preview_on_edit, name='preview_on_edit'),

        url(r'^preview/$', pages.preview, name='preview'),
        url(r'^preview_loading/$', pages.preview_loading, name='preview_loading'),

        url(r'^(\d+)/view_draft/$', pages.view_draft, name='view_draft'),
        url(r'^(\d+)/add_subpage/$', pages.add_subpage, name='add_subpage'),
        url(r'^(\d+)/delete/$', pages.delete, name='delete'),
        url(r'^(\d+)/unpublish/$', pages.unpublish, name='unpublish'),

        url(r'^search/$', pages.search, name='search'),

        url(r'^(\d+)/move/$', pages.move_choose_destination, name='move'),
        url(r'^(\d+)/move/(\d+)/$', pages.move_choose_destination, name='move_choose_destination'),
        url(r'^(\d+)/move/(\d+)/confirm/$', pages.move_confirm, name='move_confirm'),
        url(r'^(\d+)/set_position/$', pages.set_page_position, name='set_page_position'),

        url(r'^(\d+)/copy/$', pages.copy, name='copy'),

        url(r'^moderation/(\d+)/approve/$', pages.approve_moderation, name='approve_moderation'),
        url(r'^moderation/(\d+)/reject/$', pages.reject_moderation, name='reject_moderation'),
        url(r'^moderation/(\d+)/preview/$', pages.preview_for_moderation, name='preview_for_moderation'),

        url(r'^(\d+)/privacy/$', page_privacy.set_privacy, name='set_privacy'),

        url(r'^(\d+)/lock/$', pages.lock, name='lock'),
        url(r'^(\d+)/unlock/$', pages.unlock, name='unlock'),
    ], namespace='wagtailadmin_pages')),

    # TODO: Move into wagtailadmin_pages namespace
    url(r'^choose-page/$', chooser.browse, name='wagtailadmin_choose_page'),
    url(r'^choose-page/(\d+)/$', chooser.browse, name='wagtailadmin_choose_page_child'),
    url(r'^choose-page/search/$', chooser.search, name='wagtailadmin_choose_page_search'),
    url(r'^choose-external-link/$', chooser.external_link, name='wagtailadmin_choose_page_external_link'),
    url(r'^choose-email-link/$', chooser.email_link, name='wagtailadmin_choose_page_email_link'),

    url(r'^tag-autocomplete/$', tags.autocomplete, name='wagtailadmin_tag_autocomplete'),

    url(r'^account/$', account.account, name='wagtailadmin_account'),
    url(r'^account/change_password/$', account.change_password, name='wagtailadmin_account_change_password'),
    url(r'^account/notification_preferences/$', account.notification_preferences, name='wagtailadmin_account_notification_preferences'),
    url(r'^logout/$', account.logout, name='wagtailadmin_logout'),
]


# Import additional urlpatterns from any apps that define a register_admin_urls hook
for fn in hooks.get_hooks('register_admin_urls'):
    urls = fn()
    if urls:
        urlpatterns += urls


# Add "wagtailadmin.access_admin" permission check
urlpatterns = decorate_urlpatterns(urlpatterns,
    permission_required(
        'wagtailadmin.access_admin',
        login_url='wagtailadmin_login'
    )
)


# These url patterns do not require an authenticated admin user
urlpatterns += [
    url(r'^login/$', account.login, name='wagtailadmin_login'),

    # These two URLs have the "permission_required" decorator applied directly
    # as they need to fail with a 403 error rather than redirect to the login page
    url(r'^userbar/(\d+)/$', userbar.for_frontend, name='wagtailadmin_userbar_frontend'),
    url(r'^userbar/moderation/(\d+)/$', userbar.for_moderation, name='wagtailadmin_userbar_moderation'),

    # Password reset
    url(
        r'^password_reset/$', django_auth_views.password_reset, {
            'template_name': 'wagtailadmin/account/password_reset/form.html',
            'email_template_name': 'wagtailadmin/account/password_reset/email.txt',
            'subject_template_name': 'wagtailadmin/account/password_reset/email_subject.txt',
            'password_reset_form': PasswordResetForm,
            'post_reset_redirect': 'wagtailadmin_password_reset_done',
        }, name='wagtailadmin_password_reset'
    ),
    url(
        r'^password_reset/done/$', django_auth_views.password_reset_done, {
            'template_name': 'wagtailadmin/account/password_reset/done.html'
        }, name='wagtailadmin_password_reset_done'
    ),
    url(
        r'^password_reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        django_auth_views.password_reset_confirm, {
            'template_name': 'wagtailadmin/account/password_reset/confirm.html',
            'post_reset_redirect': 'wagtailadmin_password_reset_complete',
        }, name='wagtailadmin_password_reset_confirm',
    ),
    url(
        r'^password_reset/complete/$', django_auth_views.password_reset_complete, {
            'template_name': 'wagtailadmin/account/password_reset/complete.html'
        }, name='wagtailadmin_password_reset_complete'
    ),
]

# Decorate all views with cache settings to prevent caching
urlpatterns = decorate_urlpatterns(urlpatterns,
    cache_control(private=True, no_cache=True, no_store=True, max_age=0)
)
