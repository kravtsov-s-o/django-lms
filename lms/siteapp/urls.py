app_name = 'siteapp'


handler404 = 'siteapp.views.custom_page_not_found_view'
handler403 = 'siteapp.views.custom_page_access_denied_view'
handler500 = 'siteapp.views.custom_server_error_view'

urlpatterns = [

]
