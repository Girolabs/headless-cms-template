from django.conf import settings
from django.http import Http404
from django.urls import path

from wagtail.api.v2.utils import BadRequestError, page_models_from_string
from wagtail.api.v2.serializers import PageSerializer
from wagtail.api.v2.views import BaseAPIViewSet
from wagtail.models import Page, PageViewRestriction, Site
from wagtail.api.v2.filters import (
    AncestorOfFilter,
    ChildOfFilter,
    DescendantOfFilter,
    FieldsFilter,
    LocaleFilter,
    OrderingFilter,
    SearchFilter,
    TranslationOfFilter,
)
from core.paginations import WagtailAPIPagination


class PagesAPIViewSet(BaseAPIViewSet):
    """
    Our custom Pages API endpoint that allows finding pages by pk or slug
    """

    pagination_class = WagtailAPIPagination
    base_serializer_class = PageSerializer
    filter_backends = [
        FieldsFilter,
        ChildOfFilter,
        AncestorOfFilter,
        DescendantOfFilter,
        OrderingFilter,
        TranslationOfFilter,
        LocaleFilter,
        SearchFilter,  # needs to be last, as SearchResults querysets cannot be filtered further
    ]
    known_query_parameters = BaseAPIViewSet.known_query_parameters.union(
        [
            "type",
            "child_of",
            "ancestor_of",
            "descendant_of",
            "translation_of",
            "locale",
            "site",
        ]
    )
    body_fields = BaseAPIViewSet.body_fields + [
        "title",
    ]
    meta_fields = BaseAPIViewSet.meta_fields + [
        "html_url",
        "slug",
        "show_in_menus",
        "seo_title",
        "search_description",
        "first_published_at",
        "alias_of",
        "parent",
    ]
    listing_default_fields = BaseAPIViewSet.listing_default_fields + [
        "title",
        "html_url",
        "slug",
        "first_published_at",
    ]
    nested_default_fields = BaseAPIViewSet.nested_default_fields + [
        "title",
    ]
    detail_only_fields = ["parent"]
    name = "pages"
    model = Page

    def detail_view(self, request, pk=None, slug=None):
        param = pk
        if slug is not None:
            self.lookup_field = "slug"
            param = slug
        return super().detail_view(request, param)

    @classmethod
    def get_listing_default_fields(cls, model):
        listing_default_fields = super().get_listing_default_fields(model)

        # When i18n is enabled, add "locale" to default fields
        if getattr(settings, "WAGTAIL_I18N_ENABLED", False):
            listing_default_fields.append("locale")

        return listing_default_fields

    @classmethod
    def get_urlpatterns(cls):
        """
        This returns a list of URL patterns for the endpoint
        """
        return [
            path("", cls.as_view({"get": "listing_view"}), name="listing"),
            path("<int:pk>/", cls.as_view({"get": "detail_view"}), name="detail"),
            path("<slug:slug>/", cls.as_view({"get": "detail_view"}), name="detail"),
            path("find/", cls.as_view({"get": "find_view"}), name="find"),
        ]

    def get_base_queryset(self):
        """
        Returns a queryset containing all pages that can be seen by this user.

        This is used as the base for get_queryset and is also used to find the
        parent pages when using the child_of and descendant_of filters as well.
        """

        request = self.request

        # Get all live pages
        queryset = Page.objects.all().live()

        # Exclude pages that the user doesn't have access to
        restricted_pages = [
            restriction.page
            for restriction in PageViewRestriction.objects.all().select_related("page")
            if not restriction.accept_request(self.request)
        ]

        # Exclude the restricted pages and their descendants from the queryset
        for restricted_page in restricted_pages:
            queryset = queryset.not_descendant_of(restricted_page, inclusive=True)

        # Check if we have a specific site to look for
        if "site" in request.GET:
            # Optionally allow querying by port
            if ":" in request.GET["site"]:
                (hostname, port) = request.GET["site"].split(":", 1)
                query = {
                    "hostname": hostname,
                    "port": port,
                }
            else:
                query = {
                    "hostname": request.GET["site"],
                }
            try:
                site = Site.objects.get(**query)
            except Site.MultipleObjectsReturned:
                raise BadRequestError(
                    "Your query returned multiple sites. Try adding a port number to your site filter."
                )
        else:
            # Otherwise, find the site from the request
            site = Site.find_for_request(self.request)

        if site:
            base_queryset = queryset
            queryset = base_queryset.descendant_of(site.root_page, inclusive=True)

            # If internationalisation is enabled, include pages from other language trees
            if getattr(settings, "WAGTAIL_I18N_ENABLED", False):
                for translation in site.root_page.get_translations():
                    queryset |= base_queryset.descendant_of(translation, inclusive=True)

        else:
            # No sites configured
            queryset = queryset.none()

        return queryset

    def get_queryset(self):
        request = self.request

        # Allow pages to be filtered to a specific type
        try:
            models = page_models_from_string(
                request.GET.get("type", "wagtailcore.Page")
            )
        except (LookupError, ValueError):
            raise BadRequestError("type doesn't exist")

        if not models:
            return self.get_base_queryset()

        elif len(models) == 1:
            # If a single page type has been specified, swap out the Page-based queryset for one based on
            # the specific page model so that we can filter on any custom APIFields defined on that model
            return models[0].objects.filter(
                id__in=self.get_base_queryset().values_list("id", flat=True)
            )

        else:  # len(models) > 1
            return self.get_base_queryset().type(*models)

    def get_object(self):
        base = super().get_object()
        return base.specific

    def find_object(self, queryset, request):
        site = Site.find_for_request(request)
        if "html_path" in request.GET and site is not None:
            path = request.GET["html_path"]
            path_components = [component for component in path.split("/") if component]

            try:
                page, _, _ = site.root_page.specific.route(request, path_components)
            except Http404:
                return

            if queryset.filter(id=page.id).exists():
                return page

        return super().find_object(queryset, request)

    def get_serializer_context(self):
        """
        The serialization context differs between listing and detail views.
        """
        context = super().get_serializer_context()
        context["base_queryset"] = self.get_base_queryset()
        return context
