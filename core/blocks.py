from django.conf import settings
from wagtail import blocks
from wagtail.documents.blocks import DocumentChooserBlock as DefaultDocumentChooserBlock
from wagtail.images.blocks import ImageChooserBlock as DefaultImageChooserBlock
from wagtail.core.models import Site


class ImageChooserBlock(DefaultImageChooserBlock):
    def get_api_representation(self, value, context=None):
        if value:
            return {
                "id": value.id,
                "title": value.title,
                "detail_url": f"{settings.WAGTAILADMIN_BASE_URL}/api/images/{value.id}/",
                "download_url": f"{settings.WAGTAILADMIN_BASE_URL}{value.file.url}",
            }
        return super().get_api_representation(value, context)


class DocumentChooserBlock(DefaultDocumentChooserBlock):
    def get_api_representation(self, value, context=None):
        if value:
            return {
                "id": value.id,
                "title": value.title,
                "detail_url": f"{settings.WAGTAILADMIN_BASE_URL}/api/documents/{value.id}/",
                "download_url": f"{settings.WAGTAILADMIN_BASE_URL}{value.file.url}",
            }
        return super().get_api_representation(value, context)


class LinkBlock(blocks.StructBlock):
    label = blocks.TextBlock(required=True, label="Título")
    url = blocks.TextBlock(required=False, label="Url")
    document = DocumentChooserBlock(required=False, label="Documento")

    class Meta:
        # template = "streams/link.html"
        icon = "link"
        label = "Enlace"


class LinkIconBlock(blocks.StructBlock):
    icon = ImageChooserBlock(
        required=False,
        label="Ícono",
        help_text="Tamaño recomendado 20x20.",
    )
    label = blocks.TextBlock(required=True, label="Título")
    url = blocks.TextBlock(required=False, label="Url")
    document = DocumentChooserBlock(required=False, label="Documento")

    class Meta:
        # template = "streams/link.html"
        icon = "link"
        label = "Enlace"


class FeaturedLinkBlock(blocks.StructBlock):
    featured = blocks.BooleanBlock(required=False, label="Destacar", default=False)
    label = blocks.TextBlock(required=True, label="Título")
    url = blocks.TextBlock(required=False, label="Url")
    document = DocumentChooserBlock(required=False, label="Documento")

    class Meta:
        # template = "streams/link.html"
        icon = "link"
        label = "Enlace"


class ButtonBlock(blocks.StructBlock):
    label = blocks.TextBlock(required=True, label="Título")
    url = blocks.TextBlock(required=False, label="Url")
    document = DocumentChooserBlock(required=False, label="Documento")

    class Meta:
        # template = "streams/button.html"
        icon = "radio-full"
        label = "Botón"


class LogoBlock(blocks.StructBlock):
    logo = ImageChooserBlock(
        required=False,
        label="Logo",
        help_text="Tamaño recomendado 120x75.",
    )
    observation = blocks.TextBlock(required=False, label="Observación")

    class Meta:
        # template = "streams/link.html"
        icon = "link"
        label = "Logo"
