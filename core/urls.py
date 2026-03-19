from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("products/", views.product_list, name="product_list"),
    path("products/<slug:slug>/", views.product_detail, name="product_detail"),
    path("production/", views.production, name="production"),
    path("contacts/", views.contacts, name="contacts"),
    path("instructions/", views.instructions_page, name="instructions"),
    path("news/", views.news_list, name="news_list"),
    path("news/<slug:slug>/", views.news_detail, name="news_detail"),

    path("account/", views.account_dashboard, name="account_dashboard"),
    path("support/new/", views.support_new_thread, name="support_new_thread"),
    path("support/thread/<int:thread_id>/", views.support_thread_detail, name="support_thread_detail"),

    path("support/thread/<int:thread_id>/messages.json",
         views.support_thread_messages_json,
         name="support_thread_messages_json"),

    path("signup/", views.signup, name="signup"),
]
