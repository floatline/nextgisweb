define([
    "dojo/_base/declare",
    "./Base",
    "openlayers/ol",
    "@nextgisweb/pyramid/i18n!",
    "@nextgisweb/pyramid/icon",
    "xstyle/css!./resources/Zoom.css"
], function (
    declare,
    Base,
    ol,
    i18n,
    icon
) {
    return declare(Base, {
        out: false, 

        constructor: function (options) {
            if (!this.out) {
                this.label = i18n.gettext("Zoom in");
                this.customIcon = '<span class="ol-control__icon">' + icon.html({glyph: 'zoom_in'}) + '</svg></span>';
            } else {
                this.label = i18n.gettext("Zoom out");
                this.customIcon = '<span class="ol-control__icon">' + icon.html({glyph: 'zoom_out'}) + '</span>';
            };

            this.interaction = new ol.interaction.DragZoom({
                condition: ol.events.condition.always,
                out: this.out
            });
            this.deactivate();
            this.display.map.olMap.addInteraction(this.interaction);
        },

        activate: function () {
            this.interaction.setActive(true);
            if (!this.out)
                this.display.mapContainer.domNode.style.cursor = "zoom-in"
            else
                this.display.mapContainer.domNode.style.cursor = "zoom-out";
        },

        deactivate: function () {
            this.interaction.setActive(false);
            this.display.mapContainer.domNode.style.cursor = "auto";
        }

    });
});
