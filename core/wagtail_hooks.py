from django.utils.html import format_html
from django.templatetags.static import static
from wagtail.core import hooks


@hooks.register("construct_page_listing_buttons")
def replace_page_listing_button_item(
    buttons, page, page_perms, is_parent=False, context=None
):
    for index, button in enumerate(buttons):
        # basic code only - recommend you find a more robust way to confirm this is the add child page button
        if button.label == "Add child page" or button.label == "Añadir página hija":
            button.label = "Añadir nuevo"
            buttons[
                index
            ] = button  # update the matched button with a new one (note. PageListingButton is used in page listing)


@hooks.register("construct_explorer_page_queryset")
def order_by_title(parent_page, pages, request):
    if "ordering" in request.GET:
        return pages
    return pages.order_by("path")  # 'path' allows you to customize your order


@hooks.register("insert_global_admin_css")
def global_admin_css():
    return format_html(
        '<link rel="stylesheet" href="{}">', static("cms-backend/css/cms-backend.css")
    )
