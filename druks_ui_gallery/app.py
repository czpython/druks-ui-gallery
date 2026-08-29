from druks.apps import App


class DruksUiGallery(App):
    name = "druks_ui_gallery"
    icon = "layout-dashboard"
    description = "Every Druks UI block, rendered from Python."
    navigation = ["overview", "examples", "blocks"]
