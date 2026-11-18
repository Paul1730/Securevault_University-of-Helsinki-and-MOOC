from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("note/add/", views.add_note, name="add_note"),
    path("note/<int:note_id>/", views.note_detail, name="note_detail"),
    path("note/<int:note_id>/delete/", views.delete_note, name="delete_note"),
    path("search/", views.search, name="search"),
    path("settings/", views.security_settings, name="security_settings"),
    path("reset/", views.reset_password, name="reset_password"),
]
