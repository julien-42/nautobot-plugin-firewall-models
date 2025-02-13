"""Models for the Firewall plugin."""
# pylint: disable=duplicate-code, too-many-lines

from django.db import models
from django.urls import reverse
from nautobot.core.models.generics import BaseModel, PrimaryModel
from nautobot.extras.models import StatusField
from nautobot.extras.utils import extras_features

from nautobot_firewall_models import choices, validators
from nautobot_firewall_models.utils import get_default_status


###########################
# Core Models
###########################


@extras_features(
    "custom_fields",
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "relationships",
    "statuses",
    "webhooks",
)
class ApplicationObject(PrimaryModel):
    """Intermediate model to aggregate underlying application items, to allow for easier management."""

    description = models.CharField(
        max_length=200,
        blank=True,
        null=True,
    )
    category = models.CharField(max_length=48, blank=True, null=True, help_text="Category of application.")
    subcategory = models.CharField(max_length=48, blank=True, null=True, help_text="Sub-category of application.")
    technology = models.CharField(max_length=48, blank=True, null=True, help_text="Type of application technology.")
    risk = models.PositiveIntegerField(blank=True, null=True, help_text="Assessed risk of the application.")
    default_type = models.CharField(
        max_length=48, blank=True, null=True, help_text="Default type, i.e. port or app-id."
    )
    name = models.CharField(max_length=100, unique=True, help_text="Name descriptor for an application object type.")
    default_ip_protocol = models.CharField(
        max_length=48, blank=True, null=True, help_text="Name descriptor for an application object type."
    )
    status = StatusField(
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_related",  # e.g. dcim_device_related
        default=get_default_status,
    )

    class Meta:
        """Meta class."""

        ordering = ["name"]
        verbose_name_plural = "Application Objects"

    def get_application_info(self):
        """Method to Return the actual ApplicationObject type."""
        keys = ["description", "category", "subcategory", "name"]
        for key in keys:
            if getattr(self, key):
                return (key, getattr(self, key))
        return (None, None)

    def get_absolute_url(self):
        """Return detail view URL."""
        return reverse("plugins:nautobot_firewall_models:applicationobject", args=[self.pk])

    def __str__(self):
        """Stringify instance."""
        return self.name

    def save(self, *args, **kwargs):
        """Overloads to enforce clear."""
        self.clean()
        super().save(*args, **kwargs)

    @property
    def application(self):  # pylint: disable=inconsistent-return-statements
        """Returns the assigned application object."""
        for i in ["description", "category", "subcategory", "name"]:
            if getattr(self, i):
                return getattr(self, i)


@extras_features(
    "custom_fields",
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "relationships",
    "statuses",
    "webhooks",
)
class ApplicationObjectGroup(PrimaryModel):
    """Groups together ApplicationObjects to better mimic grouping sets of application objects that have a some commonality."""

    description = models.CharField(max_length=200, blank=True, null=True)
    name = models.CharField(max_length=100, unique=True, help_text="Name descriptor for a group application objects.")
    application_objects = models.ManyToManyField(
        to="nautobot_firewall_models.ApplicationObject",
        blank=True,
        through="ApplicationObjectGroupM2M",
        related_name="application_object_groups",
    )
    status = StatusField(
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_related",  # e.g. dcim_device_related
        default=get_default_status,
    )

    class Meta:
        """Meta class."""

        ordering = ["name"]
        verbose_name_plural = "Application Object Groups"

    def get_absolute_url(self):
        """Return detail view URL."""
        return reverse("plugins:nautobot_firewall_models:applicationobjectgroup", args=[self.pk])

    def __str__(self):
        """Stringify instance."""
        return self.name


@extras_features(
    "custom_fields",
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "relationships",
    "statuses",
    "webhooks",
)
class ServiceObject(PrimaryModel):
    """ServiceObject matches a IANA IP Protocol with a name and optional port number (e.g. TCP HTTPS 443)."""

    description = models.CharField(
        max_length=200,
        blank=True,
    )
    name = models.CharField(max_length=100, help_text="Name of the service (e.g. HTTP)")
    port = models.CharField(
        null=True,
        blank=True,
        validators=[validators.validate_port],
        max_length=20,
        help_text="The port or port range to tie to a service (e.g. HTTP would be port 80)",
    )
    ip_protocol = models.CharField(
        choices=choices.IP_PROTOCOL_CHOICES, max_length=20, help_text="IANA IP Protocol (e.g. TCP UDP ICMP)"
    )
    status = StatusField(
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_related",  # e.g. dcim_device_related
        default=get_default_status,
    )

    class Meta:
        """Meta class."""

        ordering = ["name"]
        verbose_name_plural = "Service Objects"

    def get_absolute_url(self):
        """Return detail view URL."""
        return reverse("plugins:nautobot_firewall_models:serviceobject", args=[self.pk])

    def __str__(self):
        """Stringify instance."""
        if self.port:
            return f"{self.name} ({self.ip_protocol}/{self.port})"
        return f"{self.name} ({self.ip_protocol})"

    def save(self, *args, **kwargs):
        """Overload save to call full_clean to ensure validators run."""
        self.full_clean()
        super().save(*args, **kwargs)


@extras_features(
    "custom_fields",
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "relationships",
    "statuses",
    "webhooks",
)
class ServiceObjectGroup(PrimaryModel):
    """Groups service objects."""

    description = models.CharField(
        max_length=200,
        blank=True,
    )
    name = models.CharField(max_length=100, unique=True)
    service_objects = models.ManyToManyField(
        to="nautobot_firewall_models.ServiceObject",
        blank=True,
        through="ServiceObjectGroupM2M",
        related_name="service_object_groups",
    )
    status = StatusField(
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_related",  # e.g. dcim_device_related
        default=get_default_status,
    )

    class Meta:
        """Meta class."""

        ordering = ["name"]
        verbose_name_plural = "Service Object Groups"

    def get_absolute_url(self):
        """Return detail view URL."""
        return reverse("plugins:nautobot_firewall_models:serviceobjectgroup", args=[self.pk])

    def __str__(self):
        """Stringify instance."""
        return self.name


###########################
# Through Models
###########################


class ApplicationObjectGroupM2M(BaseModel):
    """Custom through model to on_delete=models.PROTECT to prevent deleting associated ApplicationObject if assigned to a ApplicationObjectGroup."""

    application = models.ForeignKey("nautobot_firewall_models.ApplicationObject", on_delete=models.PROTECT)
    application_group = models.ForeignKey("nautobot_firewall_models.ApplicationObjectGroup", on_delete=models.CASCADE)


class ServiceObjectGroupM2M(BaseModel):
    """Custom through model to on_delete=models.PROTECT to prevent deleting associated ServiceGroup if assigned to a PolicyRule."""

    service = models.ForeignKey("nautobot_firewall_models.ServiceObject", on_delete=models.PROTECT)
    service_group = models.ForeignKey("nautobot_firewall_models.ServiceObjectGroup", on_delete=models.CASCADE)
