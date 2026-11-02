"""Admin pages of the WALLABY module: tiles, source extraction regions and kinematic models."""

from django.contrib import admin
from django.db.models import Q
from django.db.models.aggregates import Count
from django.urls import reverse
from django.utils.html import format_html_join
from modules.core.admin.common import RunLinkColumn, link_column
from modules.core.utils.base import ModelAdmin
from modules.wallaby.models import KinematicModel, KinematicModel_3KIDNAS, SourceExtractionRegion, Tile


class TileAdmin(ModelAdmin):
    list_display = ["id", "name", "ra_deg", "dec_deg", "phase", "show_footprint", "footprint_complete"]
    search_fields = ["id", "name", "ra_deg", "dec_deg", "phase", "tileobs__obs__name", "tileobs__obs__sbid"]

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        qs = super(TileAdmin, self).get_queryset(request)
        qs = qs.annotate(footprint_complete=Count("tileobs", filter=Q(tileobs__obs__status="COMPLETED"))).order_by(
            "-footprint_complete"
        )

        return qs.filter(phase="Survey")

    def show_footprint(self, obj):
        url = reverse("admin:operations_observation_changelist")
        fmt = format_html_join(
            ", ", "<a href='{}?q={}'>{}</a>", ((url, o.obs.name, o.obs.name) for o in obj.tileobs_set.all())
        )
        return fmt

    def footprint_complete(self, obj):
        total = obj.footprint_complete
        return total

    footprint_complete.admin_order_field = "footprint_complete"
    footprint_complete.short_description = "Footprints Complete"
    show_footprint.short_description = "Footprints"


class SourceExtractionRegionAdmin(RunLinkColumn, ModelAdmin):
    list_display = ["id", "name", "ra_deg", "dec_deg", "show_tiles", "status", "run_link", "scheduled"]
    search_fields = ["id", "name", "ra_deg", "dec_deg", "status", "scheduled", "sourceextractionregiontile__tile__name"]

    def has_delete_permission(self, request, obj=None):
        return False

    def show_tiles(self, obj):
        opts = self.model._meta
        url = reverse(f"admin:{opts.app_label}_tile_changelist")
        fmt = format_html_join(
            ", ",
            "<a href='{}?q={}'>{}</a>",
            ((url, t.tile.name, t.tile.name) for t in obj.sourceextractionregiontile_set.all()),
        )
        return fmt

    show_tiles.short_description = "Tiles"


class KinematicModel_Admin(ModelAdmin):
    model = KinematicModel
    list_display = (
        "detection_id",
        "ra",
        "dec",
        "freq",
        "team_release",
        "team_release_kin",
        "vsys_model",
        "e_vsys_model",
        "x_model",
        "e_x_model",
        "y_model",
        "e_y_model",
        "ra_model",
        "e_ra_model",
        "dec_model",
        "e_dec_model",
        "inc_model",
        "e_inc_model",
        "pa_model",
        "e_pa_model",
        "pa_model_g",
        "e_pa_model_g",
        "qflag_model",
        "rad",
        "vrot_model",
        "e_vrot_model",
        "e_vrot_model_inc",
        "rad_sd",
        "sd_model",
        "e_sd_model",
        "sd_fo_model",
        "e_sd_fo_model_inc",
        "kinematic_model_download",
    )
    readonly_fields = list_display

    kinematic_model_download = link_column("wkapp_products", "Products", "WKAPP Products")


class KinematicModel_3KIDNAS_Admin(ModelAdmin):
    model = KinematicModel_3KIDNAS
    list_display = (
        "detection_id",
        "team_release",
        "team_release_kin",
        "vsys_model",
        "e_vsys_model",
        "x_model",
        "e_x_model",
        "y_model",
        "e_y_model",
        "ra_model",
        "e_ra_model",
        "dec_model",
        "e_dec_model",
        "inc_model",
        "e_inc_model",
        "pa_model",
        "e_pa_model",
        "pa_model_g",
        "e_pa_model_g",
        "vdisp_model",
        "e_vdisp_model",
        "rad",
        "vrot_model",
        "e_vrot_model",
        "rad_sd",
        "sd_model",
        "e_sd_model",
        "sdmethodflag",
        "rhi_flag",
        "rhi_as",
        "rhi_low_as",
        "rhi_high_as",
        "dist_model",
        "rhi_kpc",
        "rhi_low_kpc",
        "rhi_high_kpc",
        "vhi_flag",
        "vhi",
        "e_vhi",
        "kflag",
        "kinver",
        "kinematic_model_3kidnas_download",
    )
    readonly_fields = list_display

    kinematic_model_3kidnas_download = link_column("wrkp_products", "Products", "WRKP Products")


admin.site.register(SourceExtractionRegion, SourceExtractionRegionAdmin)
admin.site.register(Tile, TileAdmin)
admin.site.register(KinematicModel, KinematicModel_Admin)
admin.site.register(KinematicModel_3KIDNAS, KinematicModel_3KIDNAS_Admin)
