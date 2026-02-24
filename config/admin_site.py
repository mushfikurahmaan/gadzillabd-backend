from django.contrib.admin import AdminSite

# Defines the sidebar order and grouping.
# - app_label: the Django app that owns the models
# - name: display name shown in the sidebar
# - section_key: unique key for the section (used for CSS class; needed when
#   the same app_label appears more than once, e.g. products split into two)
# - models: list of object_name strings (lowercase) to include, or None for all
SECTION_CONFIG = [
    {
        "app_label": "orders",
        "name": "Orders",
        "section_key": "orders",
        "models": None,
    },
    {
        "app_label": "products",
        "name": "Products",
        "section_key": "products",
        "models": ["product", "brand"],
    },
    {
        "app_label": "products",
        "name": "Categories",
        "section_key": "categories",
        "models": ["navbarcategory", "category"],
    },
    {
        "app_label": "notifications",
        "name": "Notifications",
        "section_key": "notifications",
        "models": None,
    },
    {
        "app_label": "cart",
        "name": "Cart",
        "section_key": "cart",
        "models": None,
    },
    {
        "app_label": "wishlist",
        "name": "Wishlist",
        "section_key": "wishlist",
        "models": None,
    },
    {
        "app_label": "contact",
        "name": "Contact Forms",
        "section_key": "contact",
        "models": None,
    },
]


class CustomAdminSite(AdminSite):
    site_header = "Gadzilla Administration"
    site_title = "Gadzilla Admin"
    index_title = "Dashboard"

    def get_app_list(self, request, app_label=None):
        app_dict = self._build_app_dict(request, app_label)
        result = []

        for section in SECTION_CONFIG:
            label = section["app_label"]
            if label not in app_dict:
                continue

            app_data = app_dict[label]
            model_filter = section.get("models")

            if model_filter is None:
                filtered_models = sorted(app_data["models"], key=lambda m: m["name"])
            else:
                filtered_models = [
                    m for m in app_data["models"]
                    if m["object_name"].lower() in model_filter
                ]
                filtered_models.sort(
                    key=lambda m: model_filter.index(m["object_name"].lower())
                )

            if not filtered_models:
                continue

            section_key = section.get("section_key", label)
            section_entry = dict(app_data)
            section_entry["name"] = section["name"]
            section_entry["app_label"] = section_key
            section_entry["models"] = filtered_models
            result.append(section_entry)

        # Append any registered apps not covered by SECTION_CONFIG (e.g. auth)
        configured_labels = {s["app_label"] for s in SECTION_CONFIG}
        for label, app_data in app_dict.items():
            if label not in configured_labels:
                result.append(app_data)

        return result


custom_admin_site = CustomAdminSite(name="custom_admin")
