from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify

from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page, Orderable
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import InlinePanel, MultiFieldPanel
from wagtail.models import Page

from core import blocks


class HomePage(Page):
    banner = models.ForeignKey(
        "wagtailimages.Image",
        verbose_name=_("Banner"),
        help_text="Tamaño recomendado: 2880 x 1400",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    sup_title = RichTextField(verbose_name=_("Título"), null=True, blank=True)
    content = RichTextField(verbose_name=_("Contenido"), null=True, blank=True)
    payment_methods = StreamField(
        [
            ("logo", blocks.LogoBlock()),
        ],
        blank=True,
        null=True,
        use_json_field=True,
        verbose_name=_("Puntos de Pago"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    content_panels = Page.content_panels + [
        FieldPanel("banner"),
        FieldPanel("sup_title"),
        InlinePanel(
            "reinsurers_items",
            label="Reaseguradora",
            heading="Reaseguradores",
            classname="collapsible, collapsed",
        ),
        FieldPanel("payment_methods", classname="collapsible, collapsed"),
    ]
    api_fields = [
        APIField("banner"),
        APIField("sup_title"),
        APIField("reinsurers_items"),
        APIField("payment_methods"),
        APIField("created_at"),
        APIField("updated_at"),
    ]
    subpage_types = []
    parent_page_types = ["wagtailcore.Page"]
    max_count = 1

    class Meta:
        verbose_name = _("Homepage")
        verbose_name_plural = _("Homepage")

    @property
    def status_string(self):
        if not self.live:
            return "BORRADOR"
        else:
            if self.has_unpublished_changes:
                return "CAMBIOS SIN PUBLICAR"
            else:
                return "PUBLICADO"


class ReinsurersItem(Orderable):
    title = models.TextField(verbose_name=_("Título"), null=True, blank=True)
    url = models.URLField(verbose_name=_("Enlace"), null=True, blank=True)
    image = models.ForeignKey(
        "wagtailimages.Image",
        verbose_name=_("Imagen"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    is_active = models.BooleanField(verbose_name=_("Activo"), default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    page = ParentalKey("HomePage", related_name="reinsurers_items")
    panels = [
        FieldPanel("image"),
        FieldPanel("is_active"),
        FieldPanel("title"),
        FieldPanel("url"),
    ]
    api_fields = [
        APIField("title"),
        APIField("url"),
        APIField("image"),
        APIField("is_active"),
        APIField("created_at"),
        APIField("updated_at"),
    ]

    class Meta:
        verbose_name = _("Reseguradora")
        verbose_name_plural = _("Reaseguradores")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        self.page = HomePage.objects.all().first()
        super(ReinsurersItem, self).save(*args, **kwargs)


class InformationPage(Page):
    full_attention = RichTextField(
        verbose_name=_("Atención 24hs"), null=True, blank=True
    )
    full_assistance = RichTextField(
        verbose_name=_("Asistencia 24hs"), null=True, blank=True
    )
    app_store_url = models.URLField(
        verbose_name=_("Link de App Store"), null=True, blank=True
    )
    google_play_url = models.URLField(
        verbose_name=_("Link de Google Play"), null=True, blank=True
    )
    messages_and_calls = RichTextField(
        verbose_name=_("Línea baja y WhatsApp"), null=True, blank=True
    )
    home_address = models.TextField(
        verbose_name=_("Dirección casa matriz"), null=True, blank=True
    )
    emails = models.TextField(verbose_name=_("Correos"), null=True, blank=True)
    opening_hours = RichTextField(
        verbose_name=_("Horarios de atención"), null=True, blank=True
    )
    facebook_url = models.URLField(
        verbose_name=_("Link a Facebook"), null=True, blank=True
    )
    instagram_url = models.URLField(
        verbose_name=_("Link a Instagram"), null=True, blank=True
    )
    linkedin_url = models.URLField(
        verbose_name=_("Link a LinkedIn"), null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    content_panels = Page.content_panels + [
        FieldPanel("full_attention"),
        FieldPanel("full_assistance"),
        MultiFieldPanel(
            [
                FieldPanel("app_store_url"),
                FieldPanel("google_play_url"),
            ],
            heading="Tiendas de apps",
            classname="collapsible",
        ),
        FieldPanel("messages_and_calls"),
        FieldPanel("home_address"),
        FieldPanel("emails"),
        FieldPanel("opening_hours"),
        MultiFieldPanel(
            [
                FieldPanel("facebook_url"),
                FieldPanel("instagram_url"),
                FieldPanel("linkedin_url"),
            ],
            heading="Redes Sociales",
            classname="collapsible",
        ),
    ]
    api_fields = [
        APIField("full_attention"),
        APIField("full_assistance"),
        APIField("app_store_url"),
        APIField("google_play_url"),
        APIField("messages_and_calls"),
        APIField("home_address"),
        APIField("emails"),
        APIField("opening_hours"),
        APIField("facebook_url"),
        APIField("instagram_url"),
        APIField("linkedin_url"),
        APIField("created_at"),
        APIField("updated_at"),
    ]
    subpage_types = []
    parent_page_types = ["wagtailcore.Page"]
    max_count = 1

    class Meta:
        verbose_name = _("Informaciones")
        verbose_name_plural = _("Informaciones")

    @property
    def status_string(self):
        if not self.live:
            return "BORRADOR"
        else:
            if self.has_unpublished_changes:
                return "CAMBIOS SIN PUBLICAR"
            else:
                return "PUBLICADO"


class FooterDocumentItemFirstColumn(Orderable):
    title = models.TextField(verbose_name=_("Título"))
    url = models.URLField(verbose_name=_("URL"), null=True, blank=True)
    featured = models.BooleanField(verbose_name=_("Destacar"), default=False)
    document = models.ForeignKey(
        "wagtaildocs.Document",
        verbose_name=_("Documento"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    page = ParentalKey("FooterPage", related_name="footer_document_first_column")
    panels = [
        FieldPanel("title"),
        FieldPanel("featured"),
        FieldPanel("document"),
        FieldPanel("url"),
    ]
    api_fields = [
        APIField("title"),
        APIField("url"),
        APIField("document"),
        APIField("featured"),
        APIField("created_at"),
        APIField("updated_at"),
    ]

    class Meta:
        verbose_name = _("Documento")
        verbose_name_plural = _("Documentos")
        ordering = ["sort_order"]


class FooterDocumentItemSecondColumn(Orderable):
    title = models.TextField(verbose_name=_("Título"))
    url = models.URLField(verbose_name=_("URL"), null=True, blank=True)
    featured = models.BooleanField(verbose_name=_("Destacar"), default=False)
    document = models.ForeignKey(
        "wagtaildocs.Document",
        verbose_name=_("Documento"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    page = ParentalKey("FooterPage", related_name="footer_document_second_column")
    panels = [
        FieldPanel("title"),
        FieldPanel("featured"),
        FieldPanel("document"),
        FieldPanel("url"),
    ]
    api_fields = [
        APIField("title"),
        APIField("url"),
        APIField("document"),
        APIField("featured"),
        APIField("created_at"),
        APIField("updated_at"),
    ]

    class Meta:
        verbose_name = _("Documento")
        verbose_name_plural = _("Documentos")
        ordering = ["sort_order"]


class FooterPage(Page):
    footer_links = StreamField(
        [
            ("link", blocks.LinkBlock()),
        ],
        blank=True,
        null=True,
        use_json_field=True,
        verbose_name=_("Enlaces"),
    )

    content_panels = Page.content_panels + [
        InlinePanel(
            "footer_document_first_column",
            heading="Documentos Primera Columna",
            label="Documento",
            classname="collapsible collapsed",
        ),
        InlinePanel(
            "footer_document_second_column",
            heading="Documentos Segunda Columna",
            label="Documento",
            classname="collapsible collapsed",
        ),
        MultiFieldPanel(
            [
                FieldPanel("footer_links"),
            ],
            heading="Enlaces extra",
            classname="collapsible collapsed",
        ),
    ]
    api_fields = [
        APIField("footer_document_first_column"),
        APIField("footer_document_second_column"),
        APIField("footer_links"),
    ]
    subpage_types = []
    parent_page_types = ["wagtailcore.Page"]
    max_count = 1

    class Meta:
        verbose_name = _("Footer")
        verbose_name_plural = _("Footer")

    @property
    def status_string(self):
        if not self.live:
            return "BORRADOR"
        else:
            if self.has_unpublished_changes:
                return "CAMBIOS SIN PUBLICAR"
            else:
                return "PUBLICADO"
