from . import filters_panel, view_panel


def register() -> None:
    view_panel.register()
    filters_panel.register()


def unregister() -> None:
    view_panel.unregister()
    filters_panel.unregister()
