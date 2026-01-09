# pylint: disable=too-many-lines
import base64
from datetime import datetime, timedelta
from typing import Iterator, Any
import requests
from pyspark.sql.types import (
    StructType,
    StructField,
    LongType,
    StringType,
    BooleanType,
    ArrayType,
    DoubleType,
    TimestampType,
    DateType,
    MapType,
)


class LakeflowConnect:
    def __init__(self, options: dict[str, str]) -> None:
        """
        Initialize the Freshservice connector with connection-level options.

        Expected options:
            - api_key: API key used for Freshservice REST API authentication.
            - domain: Your Freshservice domain (e.g., 'acme' for acme.freshservice.com).
        """
        api_key = options.get("api_key")
        domain = options.get("domain")
        
        if not api_key:
            raise ValueError("Freshservice connector requires 'api_key' in options")
        if not domain:
            raise ValueError("Freshservice connector requires 'domain' in options")

        self.domain = domain.strip().rstrip(".freshservice.com")
        self.base_url = f"https://{self.domain}.freshservice.com/api/v2"
        
        # Configure Basic Authentication (API_KEY:X)
        auth_string = f"{api_key}:X"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Basic {encoded_auth}",
            "Content-Type": "application/json",
        })

    def list_tables(self) -> list[str]:
        """
        List names of all tables supported by this connector.
        """
        return [
            "tickets",
            "agents",
            "requesters",
            "groups",
            "departments",
            "assets",
            "problems",
            "changes",
            "releases",
            "locations",
            "vendors",
            "products",
            "contracts",
            "purchase_orders",
            # "service_catalog_items",
            #"solutions",
            "roles",
            "sla_policies",
            "business_hours",
            "announcements",
            # "ticket_fields",
        ]

    def _get_attachment_struct(self) -> StructType:
        """Return the attachment struct schema."""
        return StructType([
            StructField("id", LongType(), True),
            StructField("content_type", StringType(), True),
            StructField("size", LongType(), True),
            StructField("name", StringType(), True),
            StructField("attachment_url", StringType(), True),
            StructField("created_at", StringType(), True),
            StructField("updated_at", StringType(), True),
        ])

    def _get_address_struct(self) -> StructType:
        """Return the address struct schema."""
        return StructType([
            StructField("line1", StringType(), True),
            StructField("line2", StringType(), True),
            StructField("city", StringType(), True),
            StructField("state", StringType(), True),
            StructField("country", StringType(), True),
            StructField("zipcode", StringType(), True),
        ])

    def get_table_schema(self, table_name: str, table_options: dict[str, str]) -> StructType:
        """
        Fetch the schema of a table.
        """
        schema_map = {
            "tickets": self._get_tickets_schema,
            "agents": self._get_agents_schema,
            "requesters": self._get_requesters_schema,
            "groups": self._get_groups_schema,
            "departments": self._get_departments_schema,
            "assets": self._get_assets_schema,
            "problems": self._get_problems_schema,
            "changes": self._get_changes_schema,
            "releases": self._get_releases_schema,
            "locations": self._get_locations_schema,
            "vendors": self._get_vendors_schema,
            "products": self._get_products_schema,
            "contracts": self._get_contracts_schema,
            "purchase_orders": self._get_purchase_orders_schema,
            # "service_catalog_items": self._get_service_catalog_items_schema,
            #"solutions": self._get_solutions_schema,
            "roles": self._get_roles_schema,
            "sla_policies": self._get_sla_policies_schema,
            "business_hours": self._get_business_hours_schema,
            "announcements": self._get_announcements_schema,
            # "ticket_fields": self._get_ticket_fields_schema,
        }

        if table_name not in schema_map:
            raise ValueError(f"Unsupported table: {table_name!r}")
        return schema_map[table_name]()

    def _get_tickets_schema(self) -> StructType:
        """Return the tickets table schema."""
        attachment_struct = self._get_attachment_struct()
        return StructType([
            StructField("id", LongType(), False),
            StructField("workspace_id", LongType(), True),
            StructField("subject", StringType(), True),
            StructField("description", StringType(), True),
            StructField("description_text", StringType(), True),
            StructField("type", StringType(), True),
            StructField("status", LongType(), True),
            StructField("priority", LongType(), True),
            StructField("source", LongType(), True),
            StructField("requester_id", LongType(), True),
            StructField("responder_id", LongType(), True),
            StructField("group_id", LongType(), True),
            StructField("department_id", LongType(), True),
            StructField("company_id", LongType(), True),
            StructField("product_id", LongType(), True),
            StructField("category", StringType(), True),
            StructField("sub_category", StringType(), True),
            StructField("item_category", StringType(), True),
            StructField("impact", LongType(), True),
            StructField("urgency", LongType(), True),
            StructField("due_by", StringType(), True),
            StructField("fr_due_by", StringType(), True),
            StructField("is_escalated", BooleanType(), True),
            StructField("fr_escalated", BooleanType(), True),
            StructField("spam", BooleanType(), True),
            StructField("deleted", BooleanType(), True),
            StructField("email", StringType(), True),
            StructField("phone", StringType(), True),
            StructField("email_config_id", LongType(), True),
            StructField("sla_policy_id", LongType(), True),
            StructField("cc_emails", ArrayType(StringType(), True), True),
            StructField("fwd_emails", ArrayType(StringType(), True), True),
            StructField("reply_cc_emails", ArrayType(StringType(), True), True),
            StructField("to_emails", ArrayType(StringType(), True), True),
            StructField("attachments", ArrayType(attachment_struct, True), True),
            StructField("custom_fields", MapType(StringType(), StringType(), True), True),
            StructField("tags", ArrayType(StringType(), True), True),
            StructField("created_at", StringType(), True),
            StructField("updated_at", StringType(), True),
        ])

    def _get_agents_schema(self) -> StructType:
        """Return the agents table schema."""
        return StructType([
            StructField("id", LongType(), False),
            StructField("first_name", StringType(), True),
            StructField("last_name", StringType(), True),
            StructField("email", StringType(), True),
            StructField("job_title", StringType(), True),
            StructField("phone", StringType(), True),
            StructField("mobile_phone_number", StringType(), True),
            StructField("department_ids", ArrayType(LongType(), True), True),
            StructField("reporting_manager_id", LongType(), True),
            StructField("address", StringType(), True),
            StructField("time_zone", StringType(), True),
            StructField("time_format", StringType(), True),
            StructField("language", StringType(), True),
            StructField("location_id", LongType(), True),
            StructField("background_information", StringType(), True),
            StructField("scoreboard_level_id", LongType(), True),
            StructField("member_of", ArrayType(LongType(), True), True),
            StructField("observer_of", ArrayType(LongType(), True), True),
            StructField("role_ids", ArrayType(LongType(), True), True),
            StructField("active", BooleanType(), True),
            StructField("occasional", BooleanType(), True),
            StructField("signature", StringType(), True),
            StructField("custom_fields", MapType(StringType(), StringType(), True), True),
            StructField("created_at", StringType(), True),
            StructField("updated_at", StringType(), True),
        ])

    def _get_requesters_schema(self) -> StructType:
        """Return the requesters table schema."""
        return StructType([
            StructField("id", LongType(), False),
            StructField("first_name", StringType(), True),
            StructField("last_name", StringType(), True),
            StructField("primary_email", StringType(), True),
            StructField("secondary_emails", ArrayType(StringType(), True), True),
            StructField("job_title", StringType(), True),
            StructField("phone", StringType(), True),
            StructField("mobile_phone_number", StringType(), True),
            StructField("department_ids", ArrayType(LongType(), True), True),
            StructField("reporting_manager_id", LongType(), True),
            StructField("address", StringType(), True),
            StructField("time_zone", StringType(), True),
            StructField("time_format", StringType(), True),
            StructField("language", StringType(), True),
            StructField("location_id", LongType(), True),
            StructField("background_information", StringType(), True),
            StructField("can_see_all_tickets_from_associated_departments", BooleanType(), True),
            StructField("active", BooleanType(), True),
            StructField("vip_user", BooleanType(), True),
            StructField("custom_fields", MapType(StringType(), StringType(), True), True),
            StructField("created_at", StringType(), True),
            StructField("updated_at", StringType(), True),
        ])

    def _get_groups_schema(self) -> StructType:
        """Return the groups table schema."""
        return StructType([
            StructField("id", LongType(), False),
            StructField("name", StringType(), True),
            StructField("description", StringType(), True),
            StructField("escalate_to", LongType(), True),
            StructField("unassigned_for", StringType(), True),
            StructField("business_hours_id", LongType(), True),
            StructField("agent_ids", ArrayType(LongType(), True), True),
            StructField("members", ArrayType(LongType(), True), True),
            StructField("observers", ArrayType(LongType(), True), True),
            StructField("leaders", ArrayType(LongType(), True), True),
            StructField("auto_ticket_assign", BooleanType(), True),
            StructField("restricted", BooleanType(), True),
            StructField("approval_required", BooleanType(), True),
            StructField("created_at", StringType(), True),
            StructField("updated_at", StringType(), True),
        ])

    def _get_departments_schema(self) -> StructType:
        """Return the departments table schema."""
        return StructType([
            StructField("id", LongType(), False),
            StructField("name", StringType(), True),
            StructField("description", StringType(), True),
            StructField("head_user_id", LongType(), True),
            StructField("prime_user_id", LongType(), True),
            StructField("domains", ArrayType(StringType(), True), True),
            StructField("custom_fields", MapType(StringType(), StringType(), True), True),
            StructField("created_at", StringType(), True),
            StructField("updated_at", StringType(), True),
        ])

    def _get_assets_schema(self) -> StructType:
        """Return the assets table schema."""
        return StructType([
            StructField("id", LongType(), False),
            StructField("display_id", LongType(), True),
            StructField("name", StringType(), True),
            StructField("description", StringType(), True),
            StructField("asset_type_id", LongType(), True),
            StructField("impact", StringType(), True),
            StructField("author_type", StringType(), True),
            StructField("usage_type", StringType(), True),
            StructField("asset_tag", StringType(), True),
            StructField("user_id", LongType(), True),
            StructField("department_id", LongType(), True),
            StructField("location_id", LongType(), True),
            StructField("agent_id", LongType(), True),
            StructField("group_id", LongType(), True),
            StructField("assigned_on", StringType(), True),
            StructField("end_of_life", StringType(), True),
            StructField("discovery_enabled", BooleanType(), True),
            StructField("type_fields", MapType(StringType(), StringType(), True), True),
            StructField("created_at", StringType(), True),
            StructField("updated_at", StringType(), True),
        ])

    def _get_problems_schema(self) -> StructType:
        """Return the problems table schema."""
        return StructType([
            StructField("id", LongType(), False),
            StructField("workspace_id", LongType(), True),
            StructField("agent_id", LongType(), True),
            StructField("group_id", LongType(), True),
            StructField("description", StringType(), True),
            StructField("description_text", StringType(), True),
            StructField("requester_id", LongType(), True),
            StructField("subject", StringType(), True),
            StructField("status", LongType(), True),
            StructField("priority", LongType(), True),
            StructField("impact", LongType(), True),
            StructField("known_error", BooleanType(), True),
            StructField("due_by", StringType(), True),
            StructField("department_id", LongType(), True),
            StructField("category", StringType(), True),
            StructField("sub_category", StringType(), True),
            StructField("item_category", StringType(), True),
            StructField("analysis_fields", MapType(StringType(), StringType(), True), True),
            StructField("custom_fields", MapType(StringType(), StringType(), True), True),
            StructField("created_at", StringType(), True),
            StructField("updated_at", StringType(), True),
        ])

    def _get_changes_schema(self) -> StructType:
        """Return the changes table schema."""
        return StructType([
            StructField("id", LongType(), False),
            StructField("workspace_id", LongType(), True),
            StructField("agent_id", LongType(), True),
            StructField("group_id", LongType(), True),
            StructField("description", StringType(), True),
            StructField("description_text", StringType(), True),
            StructField("requester_id", LongType(), True),
            StructField("subject", StringType(), True),
            StructField("status", LongType(), True),
            StructField("priority", LongType(), True),
            StructField("impact", LongType(), True),
            StructField("risk", LongType(), True),
            StructField("change_type", LongType(), True),
            StructField("change_window_id", LongType(), True),
            StructField("planned_start_date", StringType(), True),
            StructField("planned_end_date", StringType(), True),
            StructField("department_id", LongType(), True),
            StructField("category", StringType(), True),
            StructField("sub_category", StringType(), True),
            StructField("item_category", StringType(), True),
            StructField("planning_fields", MapType(StringType(), StringType(), True), True),
            StructField("custom_fields", MapType(StringType(), StringType(), True), True),
            StructField("created_at", StringType(), True),
            StructField("updated_at", StringType(), True),
        ])

    def _get_releases_schema(self) -> StructType:
        """Return the releases table schema."""
        return StructType([
            StructField("id", LongType(), False),
            StructField("workspace_id", LongType(), True),
            StructField("agent_id", LongType(), True),
            StructField("group_id", LongType(), True),
            StructField("description", StringType(), True),
            StructField("description_text", StringType(), True),
            StructField("subject", StringType(), True),
            StructField("status", LongType(), True),
            StructField("priority", LongType(), True),
            StructField("release_type", LongType(), True),
            StructField("planned_start_date", StringType(), True),
            StructField("planned_end_date", StringType(), True),
            StructField("work_start_date", StringType(), True),
            StructField("work_end_date", StringType(), True),
            StructField("department_id", LongType(), True),
            StructField("category", StringType(), True),
            StructField("sub_category", StringType(), True),
            StructField("item_category", StringType(), True),
            StructField("planning_fields", MapType(StringType(), StringType(), True), True),
            StructField("custom_fields", MapType(StringType(), StringType(), True), True),
            StructField("created_at", StringType(), True),
            StructField("updated_at", StringType(), True),
        ])

    def _get_locations_schema(self) -> StructType:
        """Return the locations table schema."""
        address_struct = self._get_address_struct()
        return StructType([
            StructField("id", LongType(), False),
            StructField("name", StringType(), True),
            StructField("parent_location_id", LongType(), True),
            StructField("primary_contact_id", LongType(), True),
            StructField("address", address_struct, True),
            StructField("created_at", StringType(), True),
            StructField("updated_at", StringType(), True),
        ])

    def _get_vendors_schema(self) -> StructType:
        """Return the vendors table schema."""
        address_struct = self._get_address_struct()
        return StructType([
            StructField("id", LongType(), False),
            StructField("name", StringType(), True),
            StructField("description", StringType(), True),
            StructField("primary_contact_id", LongType(), True),
            StructField("address", address_struct, True),
            StructField("custom_fields", MapType(StringType(), StringType(), True), True),
            StructField("created_at", StringType(), True),
            StructField("updated_at", StringType(), True),
        ])

    def _get_products_schema(self) -> StructType:
        """Return the products table schema."""
        return StructType([
            StructField("id", LongType(), False),
            StructField("name", StringType(), True),
            StructField("asset_type_id", LongType(), True),
            StructField("manufacturer", StringType(), True),
            StructField("status", StringType(), True),
            StructField("mode_of_procurement", StringType(), True),
            StructField("depreciation_type_id", LongType(), True),
            StructField("description", StringType(), True),
            StructField("created_at", StringType(), True),
            StructField("updated_at", StringType(), True),
        ])

    def _get_contracts_schema(self) -> StructType:
        """Return the contracts table schema."""
        item_cost_detail_struct = StructType([
            StructField("item_name", StringType(), True),
            StructField("cost", DoubleType(), True),
            StructField("count", LongType(), True),
        ])
        return StructType([
            StructField("id", LongType(), False),
            StructField("name", StringType(), True),
            StructField("description", StringType(), True),
            StructField("vendor_id", LongType(), True),
            StructField("auto_renew", BooleanType(), True),
            StructField("notify_expiry", BooleanType(), True),
            StructField("notify_before", LongType(), True),
            StructField("approver_id", LongType(), True),
            StructField("start_date", StringType(), True),
            StructField("end_date", StringType(), True),
            StructField("cost", DoubleType(), True),
            StructField("status", StringType(), True),
            StructField("contract_number", StringType(), True),
            StructField("contract_type_id", LongType(), True),
            StructField("visible_to_id", LongType(), True),
            StructField("notify_to", ArrayType(StringType(), True), True),
            StructField("custom_fields", MapType(StringType(), StringType(), True), True),
            StructField("software_id", LongType(), True),
            StructField("license_type", StringType(), True),
            StructField("billing_cycle", StringType(), True),
            StructField("license_key", StringType(), True),
            StructField("item_cost_details", ArrayType(item_cost_detail_struct, True), True),
            StructField("created_at", StringType(), True),
            StructField("updated_at", StringType(), True),
        ])

    def _get_purchase_orders_schema(self) -> StructType:
        """Return the purchase_orders table schema."""
        purchase_item_struct = StructType([
            StructField("item_type", LongType(), True),
            StructField("item_name", StringType(), True),
            StructField("item_id", LongType(), True),
            StructField("description", StringType(), True),
            StructField("cost", DoubleType(), True),
            StructField("quantity", LongType(), True),
            StructField("received", LongType(), True),
            StructField("tax_percentage", DoubleType(), True),
        ])
        return StructType([
            StructField("id", LongType(), False),
            StructField("name", StringType(), True),
            StructField("po_number", StringType(), True),
            StructField("vendor_id", LongType(), True),
            StructField("department_id", LongType(), True),
            StructField("created_by", LongType(), True),
            StructField("expected_delivery_date", StringType(), True),
            StructField("shipping_address", StringType(), True),
            StructField("billing_same_as_shipping", BooleanType(), True),
            StructField("billing_address", StringType(), True),
            StructField("currency_code", StringType(), True),
            StructField("conversion_rate", DoubleType(), True),
            StructField("discount_percentage", DoubleType(), True),
            StructField("tax_percentage", DoubleType(), True),
            StructField("shipping_cost", DoubleType(), True),
            StructField("custom_fields", MapType(StringType(), StringType(), True), True),
            StructField("purchase_items", ArrayType(purchase_item_struct, True), True),
            StructField("status", LongType(), True),
            StructField("created_at", StringType(), True),
            StructField("updated_at", StringType(), True),
        ])

    def _get_service_catalog_items_schema(self) -> StructType:
        """Return the service_catalog_items table schema."""
        custom_field_struct = StructType([
            StructField("name", StringType(), True),
            StructField("label", StringType(), True),
            StructField("field_type", StringType(), True),
            StructField("required", BooleanType(), True),
        ])
        child_item_struct = StructType([
            StructField("id", LongType(), True),
            StructField("name", StringType(), True),
            StructField("quantity", LongType(), True),
        ])
        return StructType([
            StructField("id", LongType(), False),
            StructField("name", StringType(), True),
            StructField("display_id", LongType(), True),
            StructField("description", StringType(), True),
            StructField("short_description", StringType(), True),
            StructField("cost", DoubleType(), True),
            StructField("cost_visibility", BooleanType(), True),
            StructField("delivery_time", LongType(), True),
            StructField("delivery_time_visibility", BooleanType(), True),
            StructField("category_id", LongType(), True),
            StructField("product_id", LongType(), True),
            StructField("group_visibility", LongType(), True),
            StructField("item_type", LongType(), True),
            StructField("ci_type_id", LongType(), True),
            StructField("visibility", LongType(), True),
            StructField("deleted", BooleanType(), True),
            StructField("create_child", BooleanType(), True),
            StructField("configs", MapType(StringType(), StringType(), True), True),
            StructField("icon_name", StringType(), True),
            StructField("custom_fields", ArrayType(custom_field_struct, True), True),
            StructField("child_items", ArrayType(child_item_struct, True), True),
            StructField("created_at", StringType(), True),
            StructField("updated_at", StringType(), True),
        ])

    def _get_solutions_schema(self) -> StructType:
        """Return the solutions table schema."""
        attachment_struct = self._get_attachment_struct()
        seo_data_struct = StructType([
            StructField("meta_title", StringType(), True),
            StructField("meta_description", StringType(), True),
        ])
        return StructType([
            StructField("id", LongType(), False),
            StructField("title", StringType(), True),
            StructField("description", StringType(), True),
            StructField("description_text", StringType(), True),
            StructField("status", LongType(), True),
            StructField("approval_status", LongType(), True),
            StructField("folder_id", LongType(), True),
            StructField("category_id", LongType(), True),
            StructField("agent_id", LongType(), True),
            StructField("thumbs_up", LongType(), True),
            StructField("thumbs_down", LongType(), True),
            StructField("hits", LongType(), True),
            StructField("tags", ArrayType(StringType(), True), True),
            StructField("keywords", ArrayType(StringType(), True), True),
            StructField("seo_data", seo_data_struct, True),
            StructField("attachments", ArrayType(attachment_struct, True), True),
            StructField("created_at", StringType(), True),
            StructField("updated_at", StringType(), True),
        ])

    def _get_roles_schema(self) -> StructType:
        """Return the roles table schema."""
        return StructType([
            StructField("id", LongType(), False),
            StructField("name", StringType(), True),
            StructField("description", StringType(), True),
            StructField("default", BooleanType(), True),
            StructField("created_at", StringType(), True),
            StructField("updated_at", StringType(), True),
        ])

    def _get_sla_policies_schema(self) -> StructType:
        """Return the sla_policies table schema."""
        sla_target_struct = StructType([
            StructField("priority", LongType(), True),
            StructField("respond_within", LongType(), True),
            StructField("resolve_within", LongType(), True),
        ])
        return StructType([
            StructField("id", LongType(), False),
            StructField("name", StringType(), True),
            StructField("description", StringType(), True),
            StructField("position", LongType(), True),
            StructField("is_default", BooleanType(), True),
            StructField("active", BooleanType(), True),
            StructField("deleted", BooleanType(), True),
            StructField("applicable_to", MapType(StringType(), StringType(), True), True),
            StructField("sla_targets", ArrayType(sla_target_struct, True), True),
            StructField("escalation", MapType(StringType(), StringType(), True), True),
            StructField("created_at", StringType(), True),
            StructField("updated_at", StringType(), True),
        ])

    def _get_business_hours_schema(self) -> StructType:
        """Return the business_hours table schema."""
        holiday_struct = StructType([
            StructField("holiday_name", StringType(), True),
            StructField("holiday_date", StringType(), True),
        ])
        return StructType([
            StructField("id", LongType(), False),
            StructField("name", StringType(), True),
            StructField("description", StringType(), True),
            StructField("is_default", BooleanType(), True),
            StructField("time_zone", StringType(), True),
            StructField("service_desk_hours", MapType(StringType(), StringType(), True), True),
            StructField("list_of_holidays", ArrayType(holiday_struct, True), True),
            StructField("created_at", StringType(), True),
            StructField("updated_at", StringType(), True),
        ])

    def _get_announcements_schema(self) -> StructType:
        """Return the announcements table schema."""
        return StructType([
            StructField("id", LongType(), False),
            StructField("title", StringType(), True),
            StructField("body_html", StringType(), True),
            StructField("body", StringType(), True),
            StructField("visible_from", StringType(), True),
            StructField("visible_till", StringType(), True),
            StructField("visibility", StringType(), True),
            StructField("departments", ArrayType(LongType(), True), True),
            StructField("groups", ArrayType(LongType(), True), True),
            StructField("state", StringType(), True),
            StructField("created_by", LongType(), True),
            StructField("additional_emails", ArrayType(StringType(), True), True),
            StructField("is_read", BooleanType(), True),
            StructField("send_email", BooleanType(), True),
            StructField("created_at", StringType(), True),
            StructField("updated_at", StringType(), True),
        ])

    def _get_ticket_fields_schema(self) -> StructType:
        """Return the ticket_fields table schema."""
        choice_struct = StructType([
            StructField("id", LongType(), True),
            StructField("value", StringType(), True),
            StructField("position", LongType(), True),
        ])
        nested_field_struct = StructType([
            StructField("name", StringType(), True),
            StructField("label", StringType(), True),
            StructField("type", StringType(), True),
        ])
        return StructType([
            StructField("id", LongType(), False),
            StructField("workspace_id", LongType(), True),
            StructField("name", StringType(), True),
            StructField("label", StringType(), True),
            StructField("description", StringType(), True),
            StructField("field_type", StringType(), True),
            StructField("required", BooleanType(), True),
            StructField("required_for_closure", BooleanType(), True),
            StructField("position", LongType(), True),
            StructField("default", BooleanType(), True),
            StructField("visible_in_portal", BooleanType(), True),
            StructField("editable_in_portal", BooleanType(), True),
            StructField("required_in_portal", BooleanType(), True),
            StructField("choices", ArrayType(choice_struct, True), True),
            StructField("nested_fields", ArrayType(nested_field_struct, True), True),
            StructField("sections", ArrayType(MapType(StringType(), StringType(), True), True), True),
            StructField("created_at", StringType(), True),
            StructField("updated_at", StringType(), True),
        ])

    def read_table_metadata(self, table_name: str, table_options: dict[str, str]) -> dict:
        """
        Fetch metadata for the given table.
        """
        metadata_map = {
            "tickets": {
                "primary_keys": ["id"],
                "cursor_field": "updated_at",
                "ingestion_type": "cdc",
            },
            "agents": {
                "primary_keys": ["id"],
                "cursor_field": "updated_at",
                "ingestion_type": "cdc",
            },
            "requesters": {
                "primary_keys": ["id"],
                "cursor_field": "updated_at",
                "ingestion_type": "cdc",
            },
            "groups": {
                "primary_keys": ["id"],
                "ingestion_type": "snapshot",
            },
            "departments": {
                "primary_keys": ["id"],
                "ingestion_type": "snapshot",
            },
            "assets": {
                "primary_keys": ["id"],
                "cursor_field": "updated_at",
                "ingestion_type": "cdc",
            },
            "problems": {
                "primary_keys": ["id"],
                "cursor_field": "updated_at",
                "ingestion_type": "cdc",
            },
            "changes": {
                "primary_keys": ["id"],
                "cursor_field": "updated_at",
                "ingestion_type": "cdc",
            },
            "releases": {
                "primary_keys": ["id"],
                "cursor_field": "updated_at",
                "ingestion_type": "cdc",
            },
            "locations": {
                "primary_keys": ["id"],
                "ingestion_type": "snapshot",
            },
            "vendors": {
                "primary_keys": ["id"],
                "ingestion_type": "snapshot",
            },
            "products": {
                "primary_keys": ["id"],
                "ingestion_type": "snapshot",
            },
            "contracts": {
                "primary_keys": ["id"],
                "ingestion_type": "snapshot",
            },
            "purchase_orders": {
                "primary_keys": ["id"],
                "cursor_field": "updated_at",
                "ingestion_type": "cdc",
            },
            # "service_catalog_items": {
            #     "primary_keys": ["id"],
            #     "ingestion_type": "snapshot",
            # },
            # "solutions": {
            #     "primary_keys": ["id"],
            #     "cursor_field": "updated_at",
            #     "ingestion_type": "cdc",
            # },
            "roles": {
                "primary_keys": ["id"],
                "ingestion_type": "snapshot",
            },
            "sla_policies": {
                "primary_keys": ["id"],
                "ingestion_type": "snapshot",
            },
            "business_hours": {
                "primary_keys": ["id"],
                "ingestion_type": "snapshot",
            },
            "announcements": {
                "primary_keys": ["id"],
                "ingestion_type": "snapshot",
            },
            # "ticket_fields": {
            #     "primary_keys": ["id"],
            #     "ingestion_type": "snapshot",
            # },
        }

        if table_name not in metadata_map:
            raise ValueError(f"Unsupported table: {table_name!r}")
        return metadata_map[table_name]

    def read_table(
        self, table_name: str, start_offset: dict, table_options: dict[str, str]
    ) -> (Iterator[dict], dict):
        """
        Read records from a table and return raw JSON-like dictionaries.
        """
        reader_map = {
            "tickets": self._read_tickets,
            "agents": self._read_agents,
            "requesters": self._read_requesters,
            "groups": self._read_groups,
            "departments": self._read_departments,
            "assets": self._read_assets,
            "problems": self._read_problems,
            "changes": self._read_changes,
            "releases": self._read_releases,
            "locations": self._read_locations,
            "vendors": self._read_vendors,
            "products": self._read_products,
            "contracts": self._read_contracts,
            "purchase_orders": self._read_purchase_orders,
            # "service_catalog_items": self._read_service_catalog_items,
            #"solutions": self._read_solutions,
            "roles": self._read_roles,
            "sla_policies": self._read_sla_policies,
            "business_hours": self._read_business_hours,
            "announcements": self._read_announcements,
            #"ticket_fields": self._read_ticket_fields,
        }

        if table_name not in reader_map:
            raise ValueError(f"Unsupported table: {table_name!r}")
        return reader_map[table_name](start_offset, table_options)

    def _read_tickets(
        self, start_offset: dict, table_options: dict[str, str]
    ) -> (Iterator[dict], dict):
        """Internal implementation for reading the tickets table."""
        return self._read_paginated_with_updated_since(
            endpoint="/tickets",
            start_offset=start_offset,
            table_options=table_options,
            cursor_field="updated_at",
        )

    def _read_agents(
        self, start_offset: dict, table_options: dict[str, str]
    ) -> (Iterator[dict], dict):
        """Internal implementation for reading the agents table."""
        return self._read_paginated_with_updated_since(
            endpoint="/agents",
            start_offset=start_offset,
            table_options=table_options,
            cursor_field="updated_at",
        )

    def _read_requesters(
        self, start_offset: dict, table_options: dict[str, str]
    ) -> (Iterator[dict], dict):
        """Internal implementation for reading the requesters table."""
        return self._read_paginated_with_updated_since(
            endpoint="/requesters",
            start_offset=start_offset,
            table_options=table_options,
            cursor_field="updated_at",
        )

    def _read_groups(
        self, start_offset: dict, table_options: dict[str, str]
    ) -> (Iterator[dict], dict):
        """Internal implementation for reading the groups table."""
        return self._read_paginated_snapshot(
            endpoint="/groups",
            table_options=table_options,
        )

    def _read_departments(
        self, start_offset: dict, table_options: dict[str, str]
    ) -> (Iterator[dict], dict):
        """Internal implementation for reading the departments table."""
        return self._read_paginated_snapshot(
            endpoint="/departments",
            table_options=table_options,
        )

    def _read_assets(
        self, start_offset: dict, table_options: dict[str, str]
    ) -> (Iterator[dict], dict):
        """Internal implementation for reading the assets table."""
        return self._read_paginated_with_updated_since(
            endpoint="/assets",
            start_offset=start_offset,
            table_options=table_options,
            cursor_field="updated_at",
        )

    def _read_problems(
        self, start_offset: dict, table_options: dict[str, str]
    ) -> (Iterator[dict], dict):
        """Internal implementation for reading the problems table."""
        return self._read_paginated_with_updated_since(
            endpoint="/problems",
            start_offset=start_offset,
            table_options=table_options,
            cursor_field="updated_at",
        )

    def _read_changes(
        self, start_offset: dict, table_options: dict[str, str]
    ) -> (Iterator[dict], dict):
        """Internal implementation for reading the changes table."""
        return self._read_paginated_with_updated_since(
            endpoint="/changes",
            start_offset=start_offset,
            table_options=table_options,
            cursor_field="updated_at",
        )

    def _read_releases(
        self, start_offset: dict, table_options: dict[str, str]
    ) -> (Iterator[dict], dict):
        """Internal implementation for reading the releases table."""
        return self._read_paginated_with_updated_since(
            endpoint="/releases",
            start_offset=start_offset,
            table_options=table_options,
            cursor_field="updated_at",
        )

    def _read_locations(
        self, start_offset: dict, table_options: dict[str, str]
    ) -> (Iterator[dict], dict):
        """Internal implementation for reading the locations table."""
        return self._read_paginated_snapshot(
            endpoint="/locations",
            table_options=table_options,
        )

    def _read_vendors(
        self, start_offset: dict, table_options: dict[str, str]
    ) -> (Iterator[dict], dict):
        """Internal implementation for reading the vendors table."""
        return self._read_paginated_snapshot(
            endpoint="/vendors",
            table_options=table_options,
        )

    def _read_products(
        self, start_offset: dict, table_options: dict[str, str]
    ) -> (Iterator[dict], dict):
        """Internal implementation for reading the products table."""
        return self._read_paginated_snapshot(
            endpoint="/products",
            table_options=table_options,
        )

    def _read_contracts(
        self, start_offset: dict, table_options: dict[str, str]
    ) -> (Iterator[dict], dict):
        """Internal implementation for reading the contracts table."""
        return self._read_paginated_snapshot(
            endpoint="/contracts",
            table_options=table_options,
        )

    def _read_purchase_orders(
        self, start_offset: dict, table_options: dict[str, str]
    ) -> (Iterator[dict], dict):
        """Internal implementation for reading the purchase_orders table."""
        return self._read_paginated_with_updated_since(
            endpoint="/purchase_orders",
            start_offset=start_offset,
            table_options=table_options,
            cursor_field="updated_at",
        )

    def _read_service_catalog_items(
        self, start_offset: dict, table_options: dict[str, str]
    ) -> (Iterator[dict], dict):
        """Internal implementation for reading the service_catalog_items table."""
        return self._read_paginated_snapshot(
            endpoint="/service_catalog/items",
            table_options=table_options,
        )

    def _read_solutions(
        self, start_offset: dict, table_options: dict[str, str]
    ) -> (Iterator[dict], dict):
        """Internal implementation for reading the solutions table."""
        return self._read_paginated_with_updated_since(
            endpoint="/solutions/articles",
            start_offset=start_offset,
            table_options=table_options,
            cursor_field="updated_at",
        )

    def _read_roles(
        self, start_offset: dict, table_options: dict[str, str]
    ) -> (Iterator[dict], dict):
        """Internal implementation for reading the roles table."""
        return self._read_paginated_snapshot(
            endpoint="/roles",
            table_options=table_options,
        )

    def _read_sla_policies(
        self, start_offset: dict, table_options: dict[str, str]
    ) -> (Iterator[dict], dict):
        """Internal implementation for reading the sla_policies table."""
        return self._read_paginated_snapshot(
            endpoint="/sla_policies",
            table_options=table_options,
        )

    def _read_business_hours(
        self, start_offset: dict, table_options: dict[str, str]
    ) -> (Iterator[dict], dict):
        """Internal implementation for reading the business_hours table."""
        return self._read_paginated_snapshot(
            endpoint="/business_hours",
            table_options=table_options,
        )

    def _read_announcements(
        self, start_offset: dict, table_options: dict[str, str]
    ) -> (Iterator[dict], dict):
        """Internal implementation for reading the announcements table."""
        return self._read_paginated_snapshot(
            endpoint="/announcements",
            table_options=table_options,
        )

    def _read_ticket_fields(
        self, start_offset: dict, table_options: dict[str, str]
    ) -> (Iterator[dict], dict):
        """Internal implementation for reading the ticket_fields table."""
        return self._read_paginated_snapshot(
            endpoint="/ticket_form_fields",
            table_options=table_options,
        )

    def _read_paginated_with_updated_since(
        self,
        endpoint: str,
        start_offset: dict,
        table_options: dict[str, str],
        cursor_field: str,
    ) -> (Iterator[dict], dict):
        """
        Helper method to read tables that support incremental loading via updated_since.
        """
        try:
            per_page = int(table_options.get("per_page", 100))
        except (TypeError, ValueError):
            per_page = 100
        per_page = max(1, min(per_page, 100))

        try:
            max_pages_per_batch = int(table_options.get("max_pages_per_batch", 100))
        except (TypeError, ValueError):
            max_pages_per_batch = 100

        try:
            lookback_seconds = int(table_options.get("lookback_seconds", 300))
        except (TypeError, ValueError):
            lookback_seconds = 300

        # Determine the starting cursor
        cursor = None
        if start_offset and isinstance(start_offset, dict):
            cursor = start_offset.get("cursor")
        if not cursor:
            cursor = table_options.get("start_date")

        url = f"{self.base_url}{endpoint}"
        params = {"per_page": per_page, "page": 1}
        
        if cursor:
            params["updated_since"] = cursor

        records: list[dict[str, Any]] = []
        max_updated_at: str | None = None
        pages_fetched = 0

        while pages_fetched < max_pages_per_batch:
            try:
                response = self._session.get(url, params=params, timeout=30)
                
                if response.status_code == 429: #Too Many Requests
                    # Rate limit hit, wait and retry
                    retry_after = int(response.headers.get("Retry-After", 60))
                    import time
                    time.sleep(retry_after)
                    continue
                    
                if response.status_code != 200:
                    raise RuntimeError(
                        f"Freshservice API error for {endpoint}: "
                        f"{response.status_code} {response.text}"
                    )

                data = response.json()
                
                # Freshservice wraps results in a key (usually the endpoint name pluralized)
                # Try common patterns
                items = None
                if isinstance(data, dict):
                    # Common wrapper keys
                    for key in [endpoint.strip("/").split("/")[-1], "results", "data"]:
                        if key in data:
                            items = data[key]
                            break
                    if items is None:
                        # No wrapper, assume the dict itself is the result
                        items = [data]
                elif isinstance(data, list):
                    items = data
                
                if not items:
                    # No more records
                    break

                for item in items:
                    if not isinstance(item, dict):
                        continue
                    
                    records.append(dict(item))
                    
                    # Track max cursor value
                    updated_at = item.get(cursor_field)
                    if isinstance(updated_at, str):
                        if max_updated_at is None or updated_at > max_updated_at:
                            max_updated_at = updated_at

                # Check if there are more pages
                if len(items) < per_page:
                    break
                    
                params["page"] += 1
                pages_fetched += 1

            except requests.exceptions.RequestException as e:
                raise RuntimeError(f"Network error while reading {endpoint}: {e}")

        # Compute next cursor with lookback window
        next_cursor = cursor
        if max_updated_at:
            try:
                # Parse ISO 8601 datetime
                dt = datetime.fromisoformat(max_updated_at.replace("Z", "+00:00"))
                dt_with_lookback = dt - timedelta(seconds=lookback_seconds)
                next_cursor = dt_with_lookback.strftime("%Y-%m-%dT%H:%M:%SZ")
            except Exception:
                # Fallback: use max_updated_at as-is
                next_cursor = max_updated_at

        # Return same offset if no new records to indicate end of stream
        if not records and start_offset:
            next_offset = start_offset
        else:
            next_offset = {"cursor": next_cursor} if next_cursor else {}

        return iter(records), next_offset

    def _read_paginated_snapshot(
        self,
        endpoint: str,
        table_options: dict[str, str],
    ) -> (Iterator[dict], dict):
        """
        Helper method to read snapshot tables that don't support incremental loading.
        """
        try:
            per_page = int(table_options.get("per_page", 100))
        except (TypeError, ValueError):
            per_page = 100
        per_page = max(1, min(per_page, 100))

        try:
            max_pages_per_batch = int(table_options.get("max_pages_per_batch", 100))
        except (TypeError, ValueError):
            max_pages_per_batch = 100

        url = f"{self.base_url}{endpoint}"
        params = {"per_page": per_page, "page": 1}

        records: list[dict[str, Any]] = []
        pages_fetched = 0

        while pages_fetched < max_pages_per_batch:
            try:
                response = self._session.get(url, params=params, timeout=30)
                
                if response.status_code == 429:
                    # Rate limit hit, wait and retry
                    retry_after = int(response.headers.get("Retry-After", 60))
                    import time
                    time.sleep(retry_after)
                    continue
                    
                if response.status_code != 200:
                    raise RuntimeError(
                        f"Freshservice API error for {endpoint}: "
                        f"{response.status_code} {response.text}"
                    )

                data = response.json()
                
                # Freshservice wraps results in a key
                items = None
                if isinstance(data, dict):
                    # Common wrapper keys
                    for key in [endpoint.strip("/").split("/")[-1], "results", "data"]:
                        if key in data:
                            items = data[key]
                            break
                    if items is None:
                        items = [data]
                elif isinstance(data, list):
                    items = data
                
                if not items:
                    break

                for item in items:
                    if not isinstance(item, dict):
                        continue
                    records.append(dict(item))

                # Check if there are more pages
                if len(items) < per_page:
                    break
                    
                params["page"] += 1
                pages_fetched += 1

            except requests.exceptions.RequestException as e:
                raise RuntimeError(f"Network error while reading {endpoint}: {e}")

        # Snapshot tables return empty offset
        return iter(records), {}

