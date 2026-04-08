from django.urls import path

from .views import (
    inbox_item_apply_suggestions,
    inbox_item_create,
    inbox_item_generate_suggestions,
    inbox_item_list_create,
    inbox_item_triage_update,
)


app_name = "inbox"

urlpatterns = [
    path("", inbox_item_list_create, name="item_list"),
    path("items/create/", inbox_item_create, name="item_create"),
    path(
        "items/<int:pk>/suggestions/",
        inbox_item_generate_suggestions,
        name="item_generate_suggestions",
    ),
    path(
        "items/<int:pk>/apply-suggestions/",
        inbox_item_apply_suggestions,
        name="item_apply_suggestions",
    ),
    path("items/<int:pk>/triage/", inbox_item_triage_update, name="item_triage_update"),
]
