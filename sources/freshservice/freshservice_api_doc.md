# **Freshservice API Documentation**

## **Authorization**

- **Chosen method**: API Key with Basic Authentication
- **Base URL**: `https://<your_domain>.freshservice.com/api/v2`
- **Auth placement**:
  - HTTP Basic Authentication with API Key as the username and `X` as the password
  - Alternatively, Base64-encode `<API_KEY>:X` and pass in the `Authorization: Basic <encoded_value>` header

**How to obtain API Key**:
1. Log in to your Freshservice account
2. Click on your profile picture in the top-right corner
3. Navigate to **Profile Settings**
4. Your API key will be displayed under "Your API Key" section

**Required permissions**:
- The API key inherits the permissions of the user account it belongs to
- For read-only access, the user needs at least **Agent** role with appropriate viewing permissions
- Admin access is required for some configuration endpoints

Example authenticated request:

```bash
curl -X GET \
  -u "<API_KEY>:X" \
  -H "Content-Type: application/json" \
  "https://<your_domain>.freshservice.com/api/v2/tickets"
```

Alternative with explicit Authorization header:

```bash
curl -X GET \
  -H "Authorization: Basic <base64_encoded_api_key:X>" \
  -H "Content-Type: application/json" \
  "https://<your_domain>.freshservice.com/api/v2/tickets"
```

Notes:
- Replace `<your_domain>` with your Freshservice subdomain (e.g., `acme` for `acme.freshservice.com`)
- Rate limiting varies by plan (see Rate Limits section)
- All API responses are in JSON format
- API V1 was deprecated on May 31, 2023; use API V2 only


## **Object List**

The Freshservice API provides access to various objects for IT Service Management (ITSM). The object list is **static** (defined by the connector), not discovered dynamically from an API.

### Core ITSM Objects

| Object Name | Description | Primary Endpoint | Ingestion Type |
|------------|-------------|------------------|----------------|
| `tickets` | Support tickets (incidents and service requests) | `GET /api/v2/tickets` | `cdc` |
| `problems` | Problem records linked to incidents | `GET /api/v2/problems` | `cdc` |
| `changes` | Change management requests | `GET /api/v2/changes` | `cdc` |
| `releases` | Release management records | `GET /api/v2/releases` | `cdc` |

### User & Organization Objects

| Object Name | Description | Primary Endpoint | Ingestion Type |
|------------|-------------|------------------|----------------|
| `agents` | Support agents handling tickets | `GET /api/v2/agents` | `cdc` |
| `requesters` | End-users who raise tickets | `GET /api/v2/requesters` | `cdc` |
| `groups` | Agent groups for ticket assignment | `GET /api/v2/groups` | `snapshot` |
| `departments` | Organizational departments | `GET /api/v2/departments` | `snapshot` |
| `roles` | Agent roles with permissions | `GET /api/v2/roles` | `snapshot` |

### Asset Management Objects

| Object Name | Description | Primary Endpoint | Ingestion Type |
|------------|-------------|------------------|----------------|
| `assets` | IT assets (hardware, software, etc.) | `GET /api/v2/assets` | `cdc` |
| `software` | Software installations | `GET /api/v2/applications` | `snapshot` |
| `products` | Product catalog | `GET /api/v2/products` | `snapshot` |
| `vendors` | Vendor information | `GET /api/v2/vendors` | `snapshot` |
| `contracts` | Contracts with vendors | `GET /api/v2/contracts` | `snapshot` |
| `purchase_orders` | Purchase orders | `GET /api/v2/purchase_orders` | `cdc` |

### Service Catalog & Knowledge Base

| Object Name | Description | Primary Endpoint | Ingestion Type |
|------------|-------------|------------------|----------------|
| `service_catalog_items` | Service items offered to users | `GET /api/v2/service_catalog/items` | `snapshot` |
| `solutions` | Knowledge base articles | `GET /api/v2/solutions/articles` | `cdc` |
| `solution_categories` | Knowledge base categories | `GET /api/v2/solutions/categories` | `snapshot` |
| `solution_folders` | Knowledge base folders | `GET /api/v2/solutions/folders` | `snapshot` |

### Supporting Objects

| Object Name | Description | Primary Endpoint | Ingestion Type |
|------------|-------------|------------------|----------------|
| `locations` | Physical office locations | `GET /api/v2/locations` | `snapshot` |
| `time_entries` | Time logs for tickets | `GET /api/v2/tickets/{id}/time_entries` | `append` |
| `conversations` | Ticket conversations (notes/replies) | `GET /api/v2/tickets/{id}/conversations` | `append` |
| `tasks` | Tasks associated with tickets/changes/problems | `GET /api/v2/tickets/{id}/tasks` | `cdc` |
| `announcements` | Broadcast messages to users | `GET /api/v2/announcements` | `snapshot` |

### Configuration Objects

| Object Name | Description | Primary Endpoint | Ingestion Type |
|------------|-------------|------------------|----------------|
| `ticket_fields` | Ticket field definitions | `GET /api/v2/ticket_fields` | `snapshot` |
| `sla_policies` | SLA policy definitions | `GET /api/v2/sla_policies` | `snapshot` |
| `business_hours` | Business hours configuration | `GET /api/v2/business_hours` | `snapshot` |
| `canned_responses` | Pre-defined response templates | `GET /api/v2/canned_responses` | `snapshot` |


## **Object Schema**

### General notes

- Freshservice provides a static JSON schema for resources via its REST API documentation.
- For the connector, we define **tabular schemas** per object, derived from the JSON representation.
- Nested JSON objects (e.g., `attachments`, `custom_fields`) are modeled as **nested structures/arrays** rather than being fully flattened.

---

### `tickets` object

**Source endpoint**: `GET /api/v2/tickets`

**Key behavior**:
- Returns both incidents and service requests.
- Supports filtering via `filter`, `query`, and `updated_since` parameters.
- Pagination via `page` and `per_page` parameters.

**Schema**:

| Column Name | Type | Description |
|------------|------|-------------|
| `id` | integer (64-bit) | Unique identifier for the ticket. |
| `workspace_id` | integer (64-bit) or null | ID of the workspace (for multi-workspace accounts). |
| `subject` | string | Subject or title of the ticket. |
| `description` | string or null | HTML content describing the ticket/issue. |
| `description_text` | string or null | Plain text version of the ticket description. |
| `type` | string or null | Category of the ticket (e.g., `Incident`, `Service Request`). |
| `status` | integer | Current status of the ticket. |
| `priority` | integer | Priority level of the ticket. |
| `source` | integer | Channel through which the ticket was created. |
| `requester_id` | integer (64-bit) | User ID of the requester. |
| `responder_id` | integer (64-bit) or null | ID of the assigned agent. |
| `group_id` | integer (64-bit) or null | ID of the assigned group. |
| `department_id` | integer (64-bit) or null | ID of the associated department. |
| `company_id` | integer (64-bit) or null | ID of the associated company. |
| `product_id` | integer (64-bit) or null | ID of the associated product. |
| `category` | string or null | Primary classification/category. |
| `sub_category` | string or null | Secondary classification. |
| `item_category` | string or null | Tertiary classification. |
| `impact` | integer or null | Impact level (for incidents). |
| `urgency` | integer or null | Urgency level (for incidents). |
| `due_by` | string (ISO 8601 datetime) or null | Resolution due date. |
| `fr_due_by` | string (ISO 8601 datetime) or null | First response due date. |
| `is_escalated` | boolean | Indicates SLA escalation. |
| `fr_escalated` | boolean or null | Indicates first response escalation. |
| `spam` | boolean | Indicates if marked as spam. |
| `deleted` | boolean | Indicates if deleted/trashed. |
| `email` | string or null | Requester's email address. |
| `phone` | string or null | Requester's phone number. |
| `email_config_id` | integer (64-bit) or null | Email configuration ID. |
| `sla_policy_id` | integer (64-bit) or null | SLA policy ID. |
| `cc_emails` | array\<string\> | CC email addresses. |
| `fwd_emails` | array\<string\> | Forwarded email addresses. |
| `reply_cc_emails` | array\<string\> | Reply CC email addresses. |
| `to_emails` | array\<string\> | To email addresses. |
| `attachments` | array\<struct\> | Attached files. |
| `custom_fields` | struct (map) | Custom field key-value pairs. |
| `tags` | array\<string\> | Associated tags. |
| `created_at` | string (ISO 8601 datetime) | Creation timestamp. |
| `updated_at` | string (ISO 8601 datetime) | Last update timestamp (cursor field). |

**Enumerated Values**:

| Field | Value | Label |
|-------|-------|-------|
| status | 2 | Open |
| status | 3 | Pending |
| status | 4 | Resolved |
| status | 5 | Closed |
| priority | 1 | Low |
| priority | 2 | Medium |
| priority | 3 | High |
| priority | 4 | Urgent |
| source | 1 | Email |
| source | 2 | Portal |
| source | 3 | Phone |
| source | 4 | Chat |
| source | 5 | Feedback widget |
| source | 6 | Yammer |
| source | 7 | AWS Cloudwatch |
| source | 8 | Pagerduty |
| source | 9 | Walkup |
| source | 10 | Slack |
| source | 11 | Chatbot |
| source | 12 | Workplace |
| source | 13 | Employee Onboarding |
| source | 14 | Alerts |
| source | 15 | MS Teams |
| source | 18 | Employee Offboarding |
| impact | 1 | Low |
| impact | 2 | Medium |
| impact | 3 | High |
| urgency | 1 | Low |
| urgency | 2 | Medium |
| urgency | 3 | High |

---

### `agents` object

**Source endpoint**: `GET /api/v2/agents`

**Schema**:

| Column Name | Type | Description |
|------------|------|-------------|
| `id` | integer (64-bit) | Unique identifier for the agent. |
| `first_name` | string | First name of the agent. |
| `last_name` | string or null | Last name of the agent. |
| `email` | string | Primary email address of the agent. |
| `job_title` | string or null | Job title of the agent. |
| `phone` | string or null | Phone number of the agent. |
| `mobile_phone_number` | string or null | Mobile phone number. |
| `department_ids` | array\<integer\> | IDs of departments the agent belongs to. |
| `reporting_manager_id` | integer (64-bit) or null | ID of the reporting manager. |
| `address` | string or null | Address of the agent. |
| `time_zone` | string or null | Time zone of the agent. |
| `time_format` | string or null | Time format preference. |
| `language` | string or null | Language preference. |
| `location_id` | integer (64-bit) or null | ID of the agent's location. |
| `background_information` | string or null | Background information. |
| `scoreboard_level_id` | integer or null | Gamification scoreboard level. |
| `member_of` | array\<integer\> | Group IDs the agent is a member of. |
| `observer_of` | array\<integer\> | Group IDs the agent is an observer of. |
| `role_ids` | array\<integer\> | IDs of roles assigned to the agent. |
| `active` | boolean | Indicates if the agent is active. |
| `occasional` | boolean | Indicates if the agent is an occasional agent. |
| `signature` | string or null | Email signature. |
| `custom_fields` | struct (map) | Custom field key-value pairs. |
| `created_at` | string (ISO 8601 datetime) | Creation timestamp. |
| `updated_at` | string (ISO 8601 datetime) | Last update timestamp. |

---

### `requesters` object

**Source endpoint**: `GET /api/v2/requesters`

**Schema**:

| Column Name | Type | Description |
|------------|------|-------------|
| `id` | integer (64-bit) | Unique identifier for the requester. |
| `first_name` | string | First name of the requester. |
| `last_name` | string or null | Last name of the requester. |
| `primary_email` | string | Primary email address. |
| `secondary_emails` | array\<string\> | Secondary email addresses. |
| `job_title` | string or null | Job title of the requester. |
| `phone` | string or null | Phone number. |
| `mobile_phone_number` | string or null | Mobile phone number. |
| `department_ids` | array\<integer\> | IDs of departments the requester belongs to. |
| `reporting_manager_id` | integer (64-bit) or null | ID of the reporting manager. |
| `address` | string or null | Address of the requester. |
| `time_zone` | string or null | Time zone. |
| `time_format` | string or null | Time format preference. |
| `language` | string or null | Language preference. |
| `location_id` | integer (64-bit) or null | ID of the requester's location. |
| `background_information` | string or null | Background information. |
| `can_see_all_tickets_from_associated_departments` | boolean | Permission flag. |
| `active` | boolean | Indicates if the requester is active. |
| `vip_user` | boolean | Indicates if the requester is a VIP. |
| `custom_fields` | struct (map) | Custom field key-value pairs. |
| `created_at` | string (ISO 8601 datetime) | Creation timestamp. |
| `updated_at` | string (ISO 8601 datetime) | Last update timestamp. |

---

### `groups` object

**Source endpoint**: `GET /api/v2/groups`

**Schema**:

| Column Name | Type | Description |
|------------|------|-------------|
| `id` | integer (64-bit) | Unique identifier for the group. |
| `name` | string | Name of the group. |
| `description` | string or null | Description of the group. |
| `escalate_to` | integer (64-bit) or null | ID of the group to escalate to. |
| `unassigned_for` | string or null | Auto-escalation time for unassigned tickets. |
| `business_hours_id` | integer (64-bit) or null | ID of the associated business hours. |
| `agent_ids` | array\<integer\> | IDs of agents in the group. |
| `members` | array\<integer\> | IDs of member agents. |
| `observers` | array\<integer\> | IDs of observer agents. |
| `leaders` | array\<integer\> | IDs of group leaders. |
| `auto_ticket_assign` | boolean | Indicates if auto-assignment is enabled. |
| `restricted` | boolean | Indicates if the group is restricted. |
| `approval_required` | boolean | Indicates if approval is required. |
| `created_at` | string (ISO 8601 datetime) | Creation timestamp. |
| `updated_at` | string (ISO 8601 datetime) | Last update timestamp. |

---

### `departments` object

**Source endpoint**: `GET /api/v2/departments`

**Schema**:

| Column Name | Type | Description |
|------------|------|-------------|
| `id` | integer (64-bit) | Unique identifier for the department. |
| `name` | string | Name of the department. |
| `description` | string or null | Description of the department. |
| `head_user_id` | integer (64-bit) or null | ID of the department head. |
| `prime_user_id` | integer (64-bit) or null | ID of the primary contact. |
| `domains` | array\<string\> | Email domains associated with the department. |
| `custom_fields` | struct (map) | Custom field key-value pairs. |
| `created_at` | string (ISO 8601 datetime) | Creation timestamp. |
| `updated_at` | string (ISO 8601 datetime) | Last update timestamp. |

---

### `assets` object

**Source endpoint**: `GET /api/v2/assets`

**Schema**:

| Column Name | Type | Description |
|------------|------|-------------|
| `id` | integer (64-bit) | Unique identifier for the asset. |
| `display_id` | integer | Display ID of the asset. |
| `name` | string | Name of the asset. |
| `description` | string or null | Description of the asset. |
| `asset_type_id` | integer (64-bit) | ID of the asset type. |
| `impact` | string or null | Impact level of the asset. |
| `author_type` | string or null | Type of author who created the asset. |
| `usage_type` | string or null | Usage type of the asset. |
| `asset_tag` | string or null | Asset tag identifier. |
| `user_id` | integer (64-bit) or null | ID of the user associated with the asset. |
| `department_id` | integer (64-bit) or null | ID of the department owning the asset. |
| `location_id` | integer (64-bit) or null | ID of the asset's location. |
| `agent_id` | integer (64-bit) or null | ID of the agent managing the asset. |
| `group_id` | integer (64-bit) or null | ID of the group managing the asset. |
| `assigned_on` | string (ISO 8601 datetime) or null | Date when the asset was assigned. |
| `end_of_life` | string (date) or null | End of life date. |
| `discovery_enabled` | boolean | Indicates if discovery is enabled. |
| `type_fields` | struct (map) | Type-specific fields. |
| `created_at` | string (ISO 8601 datetime) | Creation timestamp. |
| `updated_at` | string (ISO 8601 datetime) | Last update timestamp. |

---

### `problems` object

**Source endpoint**: `GET /api/v2/problems`

**Schema**:

| Column Name | Type | Description |
|------------|------|-------------|
| `id` | integer (64-bit) | Unique identifier for the problem. |
| `workspace_id` | integer (64-bit) or null | ID of the workspace. |
| `agent_id` | integer (64-bit) or null | ID of the assigned agent. |
| `group_id` | integer (64-bit) or null | ID of the assigned group. |
| `description` | string or null | HTML description of the problem. |
| `description_text` | string or null | Plain text description. |
| `requester_id` | integer (64-bit) | ID of the requester. |
| `subject` | string | Subject of the problem. |
| `status` | integer | Current status. |
| `priority` | integer | Priority level. |
| `impact` | integer | Impact level. |
| `known_error` | boolean | Indicates if this is a known error. |
| `due_by` | string (ISO 8601 datetime) or null | Due date for resolution. |
| `department_id` | integer (64-bit) or null | ID of the associated department. |
| `category` | string or null | Category of the problem. |
| `sub_category` | string or null | Sub-category. |
| `item_category` | string or null | Item category. |
| `analysis_fields` | struct or null | Root cause analysis fields. |
| `custom_fields` | struct (map) | Custom field key-value pairs. |
| `created_at` | string (ISO 8601 datetime) | Creation timestamp. |
| `updated_at` | string (ISO 8601 datetime) | Last update timestamp. |

**Enumerated Values**:

| Field | Value | Label |
|-------|-------|-------|
| status | 1 | Open |
| status | 2 | Change Requested |
| status | 3 | Closed |
| priority | 1 | Low |
| priority | 2 | Medium |
| priority | 3 | High |
| priority | 4 | Urgent |
| impact | 1 | Low |
| impact | 2 | Medium |
| impact | 3 | High |

---

### `changes` object

**Source endpoint**: `GET /api/v2/changes`

**Schema**:

| Column Name | Type | Description |
|------------|------|-------------|
| `id` | integer (64-bit) | Unique identifier for the change. |
| `workspace_id` | integer (64-bit) or null | ID of the workspace. |
| `agent_id` | integer (64-bit) or null | ID of the assigned agent. |
| `group_id` | integer (64-bit) or null | ID of the assigned group. |
| `description` | string or null | HTML description of the change. |
| `description_text` | string or null | Plain text description. |
| `requester_id` | integer (64-bit) | ID of the requester. |
| `subject` | string | Subject of the change. |
| `status` | integer | Current status. |
| `priority` | integer | Priority level. |
| `impact` | integer | Impact level. |
| `risk` | integer | Risk level. |
| `change_type` | integer | Type of change. |
| `change_window_id` | integer (64-bit) or null | ID of the change window. |
| `planned_start_date` | string (ISO 8601 datetime) or null | Planned start date. |
| `planned_end_date` | string (ISO 8601 datetime) or null | Planned end date. |
| `department_id` | integer (64-bit) or null | ID of the associated department. |
| `category` | string or null | Category of the change. |
| `sub_category` | string or null | Sub-category. |
| `item_category` | string or null | Item category. |
| `planning_fields` | struct or null | Planning phase fields. |
| `custom_fields` | struct (map) | Custom field key-value pairs. |
| `created_at` | string (ISO 8601 datetime) | Creation timestamp. |
| `updated_at` | string (ISO 8601 datetime) | Last update timestamp. |

**Enumerated Values**:

| Field | Value | Label |
|-------|-------|-------|
| status | 1 | Open |
| status | 2 | Planning |
| status | 3 | Awaiting Approval |
| status | 4 | Pending Release |
| status | 5 | Pending Review |
| status | 6 | Closed |
| priority | 1 | Low |
| priority | 2 | Medium |
| priority | 3 | High |
| priority | 4 | Urgent |
| impact | 1 | Low |
| impact | 2 | Medium |
| impact | 3 | High |
| risk | 1 | Low |
| risk | 2 | Medium |
| risk | 3 | High |
| risk | 4 | Very High |
| change_type | 1 | Minor |
| change_type | 2 | Standard |
| change_type | 3 | Major |
| change_type | 4 | Emergency |

---

### `releases` object

**Source endpoint**: `GET /api/v2/releases`

**Schema**:

| Column Name | Type | Description |
|------------|------|-------------|
| `id` | integer (64-bit) | Unique identifier for the release. |
| `workspace_id` | integer (64-bit) or null | ID of the workspace. |
| `agent_id` | integer (64-bit) or null | ID of the assigned agent. |
| `group_id` | integer (64-bit) or null | ID of the assigned group. |
| `description` | string or null | HTML description of the release. |
| `description_text` | string or null | Plain text description. |
| `subject` | string | Subject of the release. |
| `status` | integer | Current status. |
| `priority` | integer | Priority level. |
| `release_type` | integer | Type of release. |
| `planned_start_date` | string (ISO 8601 datetime) or null | Planned start date. |
| `planned_end_date` | string (ISO 8601 datetime) or null | Planned end date. |
| `work_start_date` | string (ISO 8601 datetime) or null | Actual work start date. |
| `work_end_date` | string (ISO 8601 datetime) or null | Actual work end date. |
| `department_id` | integer (64-bit) or null | ID of the associated department. |
| `category` | string or null | Category of the release. |
| `sub_category` | string or null | Sub-category. |
| `item_category` | string or null | Item category. |
| `planning_fields` | struct or null | Planning phase fields. |
| `custom_fields` | struct (map) | Custom field key-value pairs. |
| `created_at` | string (ISO 8601 datetime) | Creation timestamp. |
| `updated_at` | string (ISO 8601 datetime) | Last update timestamp. |

**Enumerated Values**:

| Field | Value | Label |
|-------|-------|-------|
| status | 1 | Open |
| status | 2 | On hold |
| status | 3 | In Progress |
| status | 4 | Incomplete |
| status | 5 | Completed |
| priority | 1 | Low |
| priority | 2 | Medium |
| priority | 3 | High |
| priority | 4 | Urgent |
| release_type | 1 | Minor |
| release_type | 2 | Standard |
| release_type | 3 | Major |
| release_type | 4 | Emergency |

---

### `locations` object

**Source endpoint**: `GET /api/v2/locations`

**Schema**:

| Column Name | Type | Description |
|------------|------|-------------|
| `id` | integer (64-bit) | Unique identifier for the location. |
| `name` | string | Name of the location. |
| `parent_location_id` | integer (64-bit) or null | ID of the parent location. |
| `primary_contact_id` | integer (64-bit) or null | ID of the primary contact. |
| `address` | struct or null | Address details (line1, line2, city, state, country, zipcode). |
| `created_at` | string (ISO 8601 datetime) | Creation timestamp. |
| `updated_at` | string (ISO 8601 datetime) | Last update timestamp. |

---

### `vendors` object

**Source endpoint**: `GET /api/v2/vendors`

**Schema**:

| Column Name | Type | Description |
|------------|------|-------------|
| `id` | integer (64-bit) | Unique identifier for the vendor. |
| `name` | string | Name of the vendor. |
| `description` | string or null | Description of the vendor. |
| `primary_contact_id` | integer (64-bit) or null | ID of the primary contact. |
| `address` | struct or null | Address details. |
| `custom_fields` | struct (map) | Custom field key-value pairs. |
| `created_at` | string (ISO 8601 datetime) | Creation timestamp. |
| `updated_at` | string (ISO 8601 datetime) | Last update timestamp. |

---

### `products` object

**Source endpoint**: `GET /api/v2/products`

**Schema**:

| Column Name | Type | Description |
|------------|------|-------------|
| `id` | integer (64-bit) | Unique identifier for the product. |
| `name` | string | Name of the product. |
| `asset_type_id` | integer (64-bit) or null | ID of the associated asset type. |
| `manufacturer` | string or null | Manufacturer name. |
| `status` | string or null | Status of the product. |
| `mode_of_procurement` | string or null | How the product is procured. |
| `depreciation_type_id` | integer (64-bit) or null | ID of the depreciation type. |
| `description` | string or null | Description of the product. |
| `created_at` | string (ISO 8601 datetime) | Creation timestamp. |
| `updated_at` | string (ISO 8601 datetime) | Last update timestamp. |

---

### `contracts` object

**Source endpoint**: `GET /api/v2/contracts`

**Schema**:

| Column Name | Type | Description |
|------------|------|-------------|
| `id` | integer (64-bit) | Unique identifier for the contract. |
| `name` | string | Name of the contract. |
| `description` | string or null | Description of the contract. |
| `vendor_id` | integer (64-bit) or null | ID of the associated vendor. |
| `auto_renew` | boolean | Indicates if auto-renewal is enabled. |
| `notify_expiry` | boolean | Indicates if expiry notifications are enabled. |
| `notify_before` | integer or null | Days before expiry to notify. |
| `approver_id` | integer (64-bit) or null | ID of the approver. |
| `start_date` | string (date) or null | Contract start date. |
| `end_date` | string (date) or null | Contract end date. |
| `cost` | number or null | Cost of the contract. |
| `status` | string or null | Status of the contract. |
| `contract_number` | string or null | Contract number. |
| `contract_type_id` | integer (64-bit) or null | ID of the contract type. |
| `visible_to_id` | integer (64-bit) or null | Visibility setting. |
| `notify_to` | array\<string\> | Email addresses to notify. |
| `custom_fields` | struct (map) | Custom field key-value pairs. |
| `software_id` | integer (64-bit) or null | ID of associated software. |
| `license_type` | string or null | Type of license. |
| `billing_cycle` | string or null | Billing cycle. |
| `license_key` | string or null | License key. |
| `item_cost_details` | array\<struct\> | Cost breakdown details. |
| `created_at` | string (ISO 8601 datetime) | Creation timestamp. |
| `updated_at` | string (ISO 8601 datetime) | Last update timestamp. |

---

### `purchase_orders` object

**Source endpoint**: `GET /api/v2/purchase_orders`

**Schema**:

| Column Name | Type | Description |
|------------|------|-------------|
| `id` | integer (64-bit) | Unique identifier for the purchase order. |
| `name` | string | Name of the purchase order. |
| `po_number` | string | Purchase order number. |
| `vendor_id` | integer (64-bit) or null | ID of the vendor. |
| `department_id` | integer (64-bit) or null | ID of the department. |
| `created_by` | integer (64-bit) | ID of the creator. |
| `expected_delivery_date` | string (date) or null | Expected delivery date. |
| `shipping_address` | string or null | Shipping address. |
| `billing_same_as_shipping` | boolean | Indicates if billing address is same as shipping. |
| `billing_address` | string or null | Billing address. |
| `currency_code` | string | Currency code (e.g., USD). |
| `conversion_rate` | number or null | Currency conversion rate. |
| `discount_percentage` | number or null | Discount percentage. |
| `tax_percentage` | number or null | Tax percentage. |
| `shipping_cost` | number or null | Shipping cost. |
| `custom_fields` | struct (map) | Custom field key-value pairs. |
| `purchase_items` | array\<struct\> | Line items in the purchase order. |
| `status` | integer | Status of the purchase order. |
| `created_at` | string (ISO 8601 datetime) | Creation timestamp. |
| `updated_at` | string (ISO 8601 datetime) | Last update timestamp. |

**Enumerated Values**:

| Field | Value | Label |
|-------|-------|-------|
| status | 20 | Open |
| status | 25 | Ordered |
| status | 30 | Received |
| status | 35 | Partially Received |
| status | 40 | Cancelled |

---

### `service_catalog_items` object

**Source endpoint**: `GET /api/v2/service_catalog/items`

**Schema**:

| Column Name | Type | Description |
|------------|------|-------------|
| `id` | integer (64-bit) | Unique identifier for the service item. |
| `name` | string | Name of the service item. |
| `display_id` | integer | Display ID of the service item. |
| `description` | string or null | Description of the service item. |
| `short_description` | string or null | Short description. |
| `cost` | number or null | Cost of the service item. |
| `cost_visibility` | boolean | Indicates if cost is visible. |
| `delivery_time` | integer or null | Delivery time in hours. |
| `delivery_time_visibility` | boolean | Indicates if delivery time is visible. |
| `category_id` | integer (64-bit) or null | ID of the category. |
| `product_id` | integer (64-bit) or null | ID of the associated product. |
| `group_visibility` | integer | Group visibility setting. |
| `item_type` | integer | Type of the item. |
| `ci_type_id` | integer (64-bit) or null | Configuration item type ID. |
| `visibility` | integer | Visibility setting. |
| `deleted` | boolean | Indicates if deleted. |
| `create_child` | boolean | Indicates if child items can be created. |
| `configs` | struct or null | Configuration settings. |
| `icon_name` | string or null | Icon name. |
| `custom_fields` | array\<struct\> | Custom field definitions. |
| `child_items` | array\<struct\> | Child service items. |
| `created_at` | string (ISO 8601 datetime) | Creation timestamp. |
| `updated_at` | string (ISO 8601 datetime) | Last update timestamp. |

---

### `solutions` object (Knowledge Base Articles)

**Source endpoint**: `GET /api/v2/solutions/articles`

**Schema**:

| Column Name | Type | Description |
|------------|------|-------------|
| `id` | integer (64-bit) | Unique identifier for the article. |
| `title` | string | Title of the article. |
| `description` | string or null | HTML content of the article. |
| `description_text` | string or null | Plain text content. |
| `status` | integer | Publication status. |
| `approval_status` | integer or null | Approval status. |
| `folder_id` | integer (64-bit) | ID of the folder containing the article. |
| `category_id` | integer (64-bit) | ID of the category. |
| `agent_id` | integer (64-bit) or null | ID of the author agent. |
| `thumbs_up` | integer | Number of thumbs up. |
| `thumbs_down` | integer | Number of thumbs down. |
| `hits` | integer | Number of views. |
| `tags` | array\<string\> | Associated tags. |
| `keywords` | array\<string\> | SEO keywords. |
| `seo_data` | struct or null | SEO metadata. |
| `attachments` | array\<struct\> | Attached files. |
| `created_at` | string (ISO 8601 datetime) | Creation timestamp. |
| `updated_at` | string (ISO 8601 datetime) | Last update timestamp. |

**Enumerated Values**:

| Field | Value | Label |
|-------|-------|-------|
| status | 1 | Draft |
| status | 2 | Published |

---

### `time_entries` object (Child of tickets)

**Source endpoint**: `GET /api/v2/tickets/{ticket_id}/time_entries`

**Schema**:

| Column Name | Type | Description |
|------------|------|-------------|
| `id` | integer (64-bit) | Unique identifier for the time entry. |
| `ticket_id` | integer (64-bit) | ID of the parent ticket (connector-derived). |
| `start_time` | string (ISO 8601 datetime) | Start time of the work. |
| `timer_running` | boolean | Indicates if timer is currently running. |
| `billable` | boolean | Indicates if the time is billable. |
| `time_spent` | string | Time spent (HH:MM format). |
| `executed_at` | string (ISO 8601 datetime) | Date when work was executed. |
| `task_id` | integer (64-bit) or null | ID of the associated task. |
| `note` | string or null | Notes about the time entry. |
| `agent_id` | integer (64-bit) | ID of the agent who logged the time. |
| `custom_fields` | struct (map) | Custom field key-value pairs. |
| `created_at` | string (ISO 8601 datetime) | Creation timestamp. |
| `updated_at` | string (ISO 8601 datetime) | Last update timestamp. |

---

### `conversations` object (Child of tickets)

**Source endpoint**: `GET /api/v2/tickets/{ticket_id}/conversations`

**Schema**:

| Column Name | Type | Description |
|------------|------|-------------|
| `id` | integer (64-bit) | Unique identifier for the conversation. |
| `ticket_id` | integer (64-bit) | ID of the parent ticket (connector-derived). |
| `user_id` | integer (64-bit) | ID of the user who created the conversation. |
| `body` | string | HTML content of the conversation. |
| `body_text` | string | Plain text content. |
| `incoming` | boolean | Indicates if this is an incoming message. |
| `private` | boolean | Indicates if this is a private note. |
| `source` | integer | Source of the conversation (same as ticket source). |
| `support_email` | string or null | Support email used. |
| `to_emails` | array\<string\> | Recipient email addresses. |
| `from_email` | string or null | Sender email address. |
| `cc_emails` | array\<string\> | CC email addresses. |
| `bcc_emails` | array\<string\> | BCC email addresses. |
| `attachments` | array\<struct\> | Attached files. |
| `created_at` | string (ISO 8601 datetime) | Creation timestamp. |
| `updated_at` | string (ISO 8601 datetime) | Last update timestamp. |

---

### `tasks` object (Child of tickets/problems/changes/releases)

**Source endpoint**: `GET /api/v2/tickets/{ticket_id}/tasks` (also available for problems, changes, releases)

**Schema**:

| Column Name | Type | Description |
|------------|------|-------------|
| `id` | integer (64-bit) | Unique identifier for the task. |
| `parent_id` | integer (64-bit) | ID of the parent object (connector-derived). |
| `parent_type` | string | Type of parent: ticket, problem, change, or release (connector-derived). |
| `agent_id` | integer (64-bit) or null | ID of the assigned agent. |
| `group_id` | integer (64-bit) or null | ID of the assigned group. |
| `status` | integer | Status of the task. |
| `title` | string | Title of the task. |
| `description` | string or null | Description of the task. |
| `notify_before` | integer or null | Minutes before due to notify. |
| `due_date` | string (ISO 8601 datetime) or null | Due date of the task. |
| `closed_at` | string (ISO 8601 datetime) or null | Closure timestamp. |
| `created_at` | string (ISO 8601 datetime) | Creation timestamp. |
| `updated_at` | string (ISO 8601 datetime) | Last update timestamp. |

**Enumerated Values**:

| Field | Value | Label |
|-------|-------|-------|
| status | 1 | Open |
| status | 2 | In Progress |
| status | 3 | Completed |

---

### `ticket_fields` object (Configuration)

**Source endpoint**: `GET /api/v2/ticket_fields`

**Schema**:

| Column Name | Type | Description |
|------------|------|-------------|
| `id` | integer (64-bit) | Unique identifier for the field. |
| `workspace_id` | integer (64-bit) or null | ID of the workspace. |
| `name` | string | Name/key of the field. |
| `label` | string | Display label of the field. |
| `description` | string or null | Description of the field. |
| `field_type` | string | Type of the field (e.g., custom_text, custom_dropdown). |
| `required` | boolean | Indicates if the field is required. |
| `required_for_closure` | boolean | Indicates if required for ticket closure. |
| `position` | integer | Display position. |
| `default` | boolean | Indicates if this is a default field. |
| `visible_in_portal` | boolean | Indicates visibility in portal. |
| `editable_in_portal` | boolean | Indicates if editable in portal. |
| `required_in_portal` | boolean | Indicates if required in portal. |
| `choices` | array\<struct\> | Available choices for dropdown fields. |
| `nested_fields` | array\<struct\> | Nested field definitions. |
| `sections` | array\<struct\> | Field sections. |
| `created_at` | string (ISO 8601 datetime) | Creation timestamp. |
| `updated_at` | string (ISO 8601 datetime) | Last update timestamp. |

---

### `roles` object

**Source endpoint**: `GET /api/v2/roles`

**Schema**:

| Column Name | Type | Description |
|------------|------|-------------|
| `id` | integer (64-bit) | Unique identifier for the role. |
| `name` | string | Name of the role. |
| `description` | string or null | Description of the role. |
| `default` | boolean | Indicates if this is a default role. |
| `created_at` | string (ISO 8601 datetime) | Creation timestamp. |
| `updated_at` | string (ISO 8601 datetime) | Last update timestamp. |

---

### `sla_policies` object

**Source endpoint**: `GET /api/v2/sla_policies`

**Schema**:

| Column Name | Type | Description |
|------------|------|-------------|
| `id` | integer (64-bit) | Unique identifier for the SLA policy. |
| `name` | string | Name of the SLA policy. |
| `description` | string or null | Description of the policy. |
| `position` | integer | Priority position. |
| `is_default` | boolean | Indicates if this is the default policy. |
| `active` | boolean | Indicates if the policy is active. |
| `deleted` | boolean | Indicates if deleted. |
| `applicable_to` | struct | Conditions for when the policy applies. |
| `sla_targets` | array\<struct\> | SLA target definitions. |
| `escalation` | struct or null | Escalation rules. |
| `created_at` | string (ISO 8601 datetime) | Creation timestamp. |
| `updated_at` | string (ISO 8601 datetime) | Last update timestamp. |

---

### `business_hours` object

**Source endpoint**: `GET /api/v2/business_hours`

**Schema**:

| Column Name | Type | Description |
|------------|------|-------------|
| `id` | integer (64-bit) | Unique identifier for the business hours config. |
| `name` | string | Name of the business hours configuration. |
| `description` | string or null | Description. |
| `is_default` | boolean | Indicates if this is the default configuration. |
| `time_zone` | string | Time zone for the business hours. |
| `service_desk_hours` | struct | Working hours for each day of the week. |
| `list_of_holidays` | array\<struct\> | List of holidays. |
| `created_at` | string (ISO 8601 datetime) | Creation timestamp. |
| `updated_at` | string (ISO 8601 datetime) | Last update timestamp. |

---

### `announcements` object

**Source endpoint**: `GET /api/v2/announcements`

**Schema**:

| Column Name | Type | Description |
|------------|------|-------------|
| `id` | integer (64-bit) | Unique identifier for the announcement. |
| `title` | string | Title of the announcement. |
| `body_html` | string | HTML content of the announcement. |
| `body` | string | Plain text content. |
| `visible_from` | string (ISO 8601 datetime) | Start date for visibility. |
| `visible_till` | string (ISO 8601 datetime) or null | End date for visibility. |
| `visibility` | string | Visibility setting (all, agents, groups). |
| `departments` | array\<integer\> | Department IDs for visibility. |
| `groups` | array\<integer\> | Group IDs for visibility. |
| `state` | string | State of the announcement (active, archived). |
| `created_by` | integer (64-bit) | ID of the creator. |
| `additional_emails` | array\<string\> | Additional email addresses. |
| `is_read` | boolean | Read status. |
| `send_email` | boolean | Indicates if email was sent. |
| `created_at` | string (ISO 8601 datetime) | Creation timestamp. |
| `updated_at` | string (ISO 8601 datetime) | Last update timestamp. |


## **Get Object Primary Keys**

Primary keys are defined **statically** based on resource schemas. There is no dedicated metadata endpoint.

| Object | Primary Key | Type |
|--------|-------------|------|
| `tickets` | `id` | integer (64-bit) |
| `agents` | `id` | integer (64-bit) |
| `requesters` | `id` | integer (64-bit) |
| `groups` | `id` | integer (64-bit) |
| `departments` | `id` | integer (64-bit) |
| `assets` | `id` | integer (64-bit) |
| `problems` | `id` | integer (64-bit) |
| `changes` | `id` | integer (64-bit) |
| `releases` | `id` | integer (64-bit) |
| `locations` | `id` | integer (64-bit) |
| `vendors` | `id` | integer (64-bit) |
| `products` | `id` | integer (64-bit) |
| `contracts` | `id` | integer (64-bit) |
| `purchase_orders` | `id` | integer (64-bit) |
| `service_catalog_items` | `id` | integer (64-bit) |
| `solutions` | `id` | integer (64-bit) |
| `time_entries` | `id` (composite with `ticket_id`) | integer (64-bit) |
| `conversations` | `id` (composite with `ticket_id`) | integer (64-bit) |
| `tasks` | `id` (composite with `parent_id`, `parent_type`) | integer (64-bit) |
| `ticket_fields` | `id` | integer (64-bit) |
| `roles` | `id` | integer (64-bit) |
| `sla_policies` | `id` | integer (64-bit) |
| `business_hours` | `id` | integer (64-bit) |
| `announcements` | `id` | integer (64-bit) |


## **Object's Ingestion Type**

| Object | Ingestion Type | Cursor Field | Rationale |
|--------|----------------|--------------|-----------|
| `tickets` | `cdc` | `updated_at` | Has `updated_since` filter and `deleted` flag. |
| `agents` | `cdc` | `updated_at` | Can be filtered by state; tracks active/inactive. |
| `requesters` | `cdc` | `updated_at` | Can be filtered by state. |
| `groups` | `snapshot` | - | Small dataset; no incremental filter. |
| `departments` | `snapshot` | - | Small dataset; no incremental filter. |
| `assets` | `cdc` | `updated_at` | Has `updated_at` field. |
| `problems` | `cdc` | `updated_at` | Has `updated_since` filter. |
| `changes` | `cdc` | `updated_at` | Has `updated_since` filter. |
| `releases` | `cdc` | `updated_at` | Has `updated_since` filter. |
| `locations` | `snapshot` | - | Small dataset; no incremental filter. |
| `vendors` | `snapshot` | - | Small dataset; no incremental filter. |
| `products` | `snapshot` | - | Small dataset; no incremental filter. |
| `contracts` | `snapshot` | - | No incremental filter available. |
| `purchase_orders` | `cdc` | `updated_at` | Has `updated_at` field. |
| `service_catalog_items` | `snapshot` | - | Small dataset; no incremental filter. |
| `solutions` | `cdc` | `updated_at` | Has `updated_at` field. |
| `time_entries` | `append` | - | Child records; append only. |
| `conversations` | `append` | - | Child records; append only. |
| `tasks` | `cdc` | `updated_at` | Can track status changes. |
| `ticket_fields` | `snapshot` | - | Configuration data. |
| `roles` | `snapshot` | - | Configuration data. |
| `sla_policies` | `snapshot` | - | Configuration data. |
| `business_hours` | `snapshot` | - | Configuration data. |
| `announcements` | `snapshot` | - | Small dataset. |


## **Read API for Data Retrieval**

### Common Query Parameters

Most list endpoints support these parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `per_page` | integer | 30 | Results per page (max 100). |
| `page` | integer | 1 | Page number. |

### Endpoints with Incremental Support (`updated_since`)

| Object | Endpoint | Incremental Parameter |
|--------|----------|----------------------|
| `tickets` | `GET /api/v2/tickets` | `updated_since` |
| `problems` | `GET /api/v2/problems` | `updated_since` |
| `changes` | `GET /api/v2/changes` | `updated_since` |
| `releases` | `GET /api/v2/releases` | - (use query filter) |
| `agents` | `GET /api/v2/agents` | Filter by `state` |
| `requesters` | `GET /api/v2/requesters` | Filter by `state` |

### Example Requests

**List Tickets (Incremental)**:
```bash
curl -X GET \
  -u "<API_KEY>:X" \
  "https://<domain>.freshservice.com/api/v2/tickets?updated_since=2025-01-01T00:00:00Z&per_page=100"
```

**List Agents**:
```bash
curl -X GET \
  -u "<API_KEY>:X" \
  "https://<domain>.freshservice.com/api/v2/agents?per_page=100"
```

**List Problems**:
```bash
curl -X GET \
  -u "<API_KEY>:X" \
  "https://<domain>.freshservice.com/api/v2/problems?per_page=100"
```

**List Changes**:
```bash
curl -X GET \
  -u "<API_KEY>:X" \
  "https://<domain>.freshservice.com/api/v2/changes?per_page=100"
```

**List Assets**:
```bash
curl -X GET \
  -u "<API_KEY>:X" \
  "https://<domain>.freshservice.com/api/v2/assets?per_page=100"
```

**List Ticket Conversations** (child endpoint):
```bash
curl -X GET \
  -u "<API_KEY>:X" \
  "https://<domain>.freshservice.com/api/v2/tickets/1/conversations"
```

**List Ticket Time Entries** (child endpoint):
```bash
curl -X GET \
  -u "<API_KEY>:X" \
  "https://<domain>.freshservice.com/api/v2/tickets/1/time_entries"
```

### Rate Limits

- Rate limits vary by Freshservice subscription plan
- Response headers provide rate limit information:
  - `X-RateLimit-Total`: Total requests allowed per minute
  - `X-RateLimit-Remaining`: Remaining requests in current window
  - `X-RateLimit-Used-CurrentRequest`: Requests consumed by current call
- HTTP 429 response when rate limited
- Implement exponential backoff for rate limit handling

### Pagination Strategy

1. Set `per_page=100` (maximum) for efficiency
2. Increment `page` parameter until empty array returned
3. For incremental syncs:
   - Use `updated_since` with cursor timestamp
   - Order by `updated_at` ascending when supported
   - Store max `updated_at` for next sync

### Handling Deletes

| Object | Delete Handling |
|--------|-----------------|
| `tickets` | Use `filter=deleted` or check `deleted` field |
| `agents` | Check `active` field |
| `requesters` | Check `active` field |
| `assets` | Assets can be deleted; check for 404 |
| `problems` | Check status |
| `changes` | Check status |
| `releases` | Check status |


## **Field Type Mapping**

| Freshservice Type | Example Fields | Connector Type | Notes |
|-------------------|----------------|----------------|-------|
| integer | `id`, `status`, `priority` | `LongType` | Use 64-bit integers |
| string | `subject`, `name`, `description` | `StringType` | UTF-8 text |
| boolean | `active`, `deleted`, `spam` | `BooleanType` | true/false |
| datetime | `created_at`, `updated_at` | `TimestampType` | ISO 8601 format |
| date | `start_date`, `end_date` | `DateType` | YYYY-MM-DD format |
| object | `custom_fields`, `address` | `StructType`/`MapType` | Nested structure |
| array | `tags`, `cc_emails` | `ArrayType` | Array of elements |
| number | `cost`, `conversion_rate` | `DoubleType` | Decimal numbers |


## **Write API**

The connector is primarily read-only. Write endpoints are available for:

| Object | Create | Update | Delete |
|--------|--------|--------|--------|
| `tickets` | POST /api/v2/tickets | PUT /api/v2/tickets/{id} | DELETE /api/v2/tickets/{id} |
| `agents` | POST /api/v2/agents | PUT /api/v2/agents/{id} | DELETE /api/v2/agents/{id} |
| `requesters` | POST /api/v2/requesters | PUT /api/v2/requesters/{id} | DELETE /api/v2/requesters/{id} |
| `assets` | POST /api/v2/assets | PUT /api/v2/assets/{id} | DELETE /api/v2/assets/{id} |
| `problems` | POST /api/v2/problems | PUT /api/v2/problems/{id} | DELETE /api/v2/problems/{id} |
| `changes` | POST /api/v2/changes | PUT /api/v2/changes/{id} | DELETE /api/v2/changes/{id} |
| `releases` | POST /api/v2/releases | PUT /api/v2/releases/{id} | DELETE /api/v2/releases/{id} |


## **Known Quirks & Edge Cases**

- **API V1 Deprecation**: API V1 was deprecated on May 31, 2023. Use API V2 only.
- **Workspace support**: `workspace_id` field only present for multi-workspace accounts.
- **Custom fields**: Custom field keys are prefixed with `cf_` (e.g., `cf_employee_id`).
- **Child objects**: `time_entries`, `conversations`, `tasks` require parent ID in endpoint path.
- **Soft deletes**: Tickets use soft deletes (`deleted` flag); can be restored.
- **Rate limiting**: Varies by plan; always check response headers.
- **Pagination limits**: Max 100 records per page.
- **Query filter limits**: Some queries limited to 30 days of data.
- **Timestamp format**: All timestamps in ISO 8601 UTC format.
- **Null vs empty**: Absent fields return `null`, not empty objects.
- **HTML content**: `description` fields contain HTML; `description_text` contains plain text.


## **Research Log**

| Source Type | URL | Accessed (UTC) | Confidence | What it confirmed |
|------------|-----|----------------|------------|-------------------|
| Official Docs | https://api.freshservice.com/ | 2026-01-08 | High | All endpoints, authentication, object schemas |
| Official Docs | https://api.freshservice.com/#ticket_attributes | 2026-01-08 | High | Ticket attributes and enumerated values |
| Official Docs | https://api.freshservice.com/#agents | 2026-01-08 | High | Agent schema and endpoints |
| Official Docs | https://api.freshservice.com/#requesters | 2026-01-08 | High | Requester schema and endpoints |
| Official Docs | https://api.freshservice.com/#assets | 2026-01-08 | High | Asset schema and endpoints |
| Official Docs | https://api.freshservice.com/#problems | 2026-01-08 | High | Problem schema and endpoints |
| Official Docs | https://api.freshservice.com/#changes | 2026-01-08 | High | Change schema and endpoints |
| Official Docs | https://api.freshservice.com/#releases | 2026-01-08 | High | Release schema and endpoints |
| Official Support | https://support.freshservice.com/support/solutions/articles/50000004220 | 2026-01-08 | High | API V1 deprecation notice |
| Official Support | https://support.freshservice.com/support/solutions/articles/50000000294 | 2026-01-08 | High | How to retrieve ticket fields |
| Web Search | Various | 2026-01-08 | Medium | Cross-verified object lists and schemas |


## **Sources and References**

- **Official Freshservice REST API Documentation** (highest confidence)
  - `https://api.freshservice.com/`
  - Covers all objects: tickets, agents, requesters, groups, departments, assets, problems, changes, releases, service catalog, solutions, etc.

- **Freshworks Developer Documentation**
  - `https://developers.freshworks.com/`

- **Freshservice Support Articles**
  - `https://support.freshservice.com/support/solutions/articles/50000004220` (API V1 deprecation)
  - `https://support.freshservice.com/support/solutions/articles/50000000294` (Ticket fields API)

When conflicts arise, **official Freshservice API documentation** is treated as the source of truth.


## **Acceptance Checklist**

- [x] All required headings present and in order.
- [x] All major objects documented with schemas.
- [x] Exactly one authentication method documented (Basic Auth with API Key).
- [x] Endpoints include params, examples, and pagination details.
- [x] Incremental strategy defined for applicable objects.
- [x] Research Log completed; Sources include full URLs.
- [x] No unverifiable claims; gaps marked as TBD where applicable.
