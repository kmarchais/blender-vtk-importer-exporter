from . import filters_panel, view_panel

def register():
    view_panel.register()
    filters_panel.register()

def unregister():
    view_panel.unregister()
    filters_panel.unregister()
