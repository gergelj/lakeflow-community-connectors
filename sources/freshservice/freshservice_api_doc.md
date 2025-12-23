# **Freshservice API Documentation**

## **Authorization**

- **Chosen method**: API Key with Basic Authentication
- **Base URL**: `https://<your_domain>.freshservice.com/api/v2`
- **Auth placement**:
  - HTTP Basic Authentication with API Key as the username and `X` as the password
  - Alternatively, Base64-encode `<API_KEY>:X` and pass in the `Authorization: Basic <encoded_value>` header

**How to obtain API Key**:
1. Log in to your Freshservice account
2. Navigate to **Profile Settings** → **API Settings**
3. Your API key will be displayed (or you can generate a new one)

**Required permissions**:
- The API key inherits the permissions of the user account it belongs to
- For read-only ticket access, the user needs at least **Agent** role with ticket viewing permissions

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


## **Object List**

For connector purposes, we treat specific Freshservice REST resources as **objects/tables**.
The object list is **static** (defined by the connector), not discovered dynamically from an API.

| Object Name | Description | Primary Endpoint | Ingestion Type |
|------------|-------------|------------------|----------------|
| `tickets` | Support tickets (incidents and service requests) | `GET /api/v2/tickets` | `cdc` (upserts based on `updated_at`) |

**Connector scope for initial implementation**:
- Step 1 focuses on the `tickets` object and documents it in detail.
- Other objects (agents, requesters, departments, groups, assets, problems, changes, releases) can be added in future extensions.

**Additional objects available in Freshservice (for future extension)**:

| Object Name | Description | Primary Endpoint | Ingestion Type (planned) |
|------------|-------------|------------------|--------------------------|
| `agents` | Support agents in the helpdesk | `GET /api/v2/agents` | `snapshot` |
| `requesters` | Users who submit tickets | `GET /api/v2/requesters` | `cdc` (TBD) |
| `departments` | Organizational departments | `GET /api/v2/departments` | `snapshot` |
| `groups` | Agent groups for ticket assignment | `GET /api/v2/groups` | `snapshot` |
| `ticket_fields` | Custom and standard ticket field definitions | `GET /api/v2/ticket_fields` | `snapshot` |


## **Object Schema**

### General notes

- Freshservice provides a static JSON schema for resources via its REST API documentation.
- For the connector, we define **tabular schemas** per object, derived from the JSON representation.
- Nested JSON objects (e.g., `attachments`, `custom_fields`) are modeled as **nested structures/arrays** rather than being fully flattened.

### `tickets` object (primary table)

**Source endpoint**:
`GET /api/v2/tickets`

**Key behavior**:
- Returns both incidents and service requests.
- Supports filtering via `filter` predefined filters, `query` custom queries, and `updated_since` for incremental reads.
- Pagination is handled via `page` and `per_page` parameters.

**High-level schema (connector view)**:

Top-level fields (all from the Freshservice REST API):

| Column Name | Type | Description |
|------------|------|-------------|
| `id` | integer (64-bit) | Unique identifier for the ticket. |
| `workspace_id` | integer (64-bit) or null | ID of the workspace to which the ticket belongs. Applicable only to accounts with workspaces enabled. |
| `subject` | string | Subject or title of the ticket. |
| `description` | string or null | HTML content describing the ticket/issue. |
| `description_text` | string or null | Plain text version of the ticket description. |
| `type` | string or null | Category of the ticket (e.g., `Incident`, `Service Request`). |
| `status` | integer | Current status of the ticket. See enumerated values below. |
| `priority` | integer | Priority level of the ticket. See enumerated values below. |
| `source` | integer | Channel through which the ticket was created. See enumerated values below. |
| `requester_id` | integer (64-bit) | User ID of the individual who raised the ticket. |
| `responder_id` | integer (64-bit) or null | ID of the agent assigned to respond to the ticket. |
| `group_id` | integer (64-bit) or null | ID of the group to which the ticket is assigned. |
| `department_id` | integer (64-bit) or null | ID of the department associated with the ticket. |
| `company_id` | integer (64-bit) or null | ID of the company associated with the ticket. |
| `product_id` | integer (64-bit) or null | ID of the product associated with the ticket. |
| `category` | string or null | Primary classification/category of the ticket. |
| `sub_category` | string or null | Secondary classification under the main category. |
| `item_category` | string or null | Tertiary classification under the sub-category. |
| `impact` | integer or null | Impact level of the ticket (for incident tickets). |
| `urgency` | integer or null | Urgency level of the ticket (for incident tickets). |
| `due_by` | string (ISO 8601 datetime) or null | Date and time by which the ticket is due to be resolved. |
| `fr_due_by` | string (ISO 8601 datetime) or null | Date and time by which the first response is due. |
| `is_escalated` | boolean | Indicates if the ticket has been escalated for SLA breach. |
| `fr_escalated` | boolean or null | Indicates if the first response time has been escalated. |
| `spam` | boolean | Indicates if the ticket has been marked as spam. |
| `deleted` | boolean | Indicates if the ticket has been deleted/trashed. |
| `email` | string or null | Email address of the requester. |
| `phone` | string or null | Phone number of the requester. |
| `email_config_id` | integer (64-bit) or null | ID of the email configuration used for the ticket. |
| `sla_policy_id` | integer (64-bit) or null | ID of the SLA policy associated with the ticket. |
| `cc_emails` | array\<string\> | Email addresses added in the 'cc' field of the incoming ticket email. |
| `fwd_emails` | array\<string\> | Email addresses to which the ticket was forwarded. |
| `reply_cc_emails` | array\<string\> | Email addresses added in the 'cc' field of ticket replies. |
| `to_emails` | array\<string\> | Email addresses in the 'to' field of the incoming ticket email. |
| `attachments` | array\<struct\> | Files attached to the ticket. Total size cannot exceed 40 MB. |
| `custom_fields` | struct (map) | Key-value pairs containing custom field data defined in the account. |
| `tags` | array\<string\> | Tags associated with the ticket. |
| `created_at` | string (ISO 8601 datetime) | Timestamp when the ticket was created. |
| `updated_at` | string (ISO 8601 datetime) | Timestamp when the ticket was last updated. Used as incremental cursor. |

**Nested `attachments` struct** (elements of `attachments` array):

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer (64-bit) | Unique identifier for the attachment. |
| `name` | string | Name of the attached file. |
| `content_type` | string | MIME type of the attachment. |
| `size` | integer | Size of the attachment in bytes. |
| `created_at` | string (ISO 8601 datetime) | Timestamp when the attachment was created. |
| `updated_at` | string (ISO 8601 datetime) | Timestamp when the attachment was last updated. |
| `attachment_url` | string | URL to download the attachment. |

**Enumerated Values**:

**Status**:
| Value | Label |
|-------|-------|
| 2 | Open |
| 3 | Pending |
| 4 | Resolved |
| 5 | Closed |

Note: Custom statuses can be defined in Freshservice and will have different numeric values.

**Priority**:
| Value | Label |
|-------|-------|
| 1 | Low |
| 2 | Medium |
| 3 | High |
| 4 | Urgent |

**Source**:
| Value | Label |
|-------|-------|
| 1 | Email |
| 2 | Portal |
| 3 | Phone |
| 4 | Chat |
| 5 | Feedback widget |
| 6 | Yammer |
| 7 | AWS Cloudwatch |
| 8 | Pagerduty |
| 9 | Walkup |
| 10 | Slack |
| 11 | Chatbot |
| 12 | Workplace |
| 13 | Employee Onboarding |
| 14 | Alerts |
| 15 | MS Teams |
| 18 | Employee Offboarding |

**Impact** (for incidents):
| Value | Label |
|-------|-------|
| 1 | Low |
| 2 | Medium |
| 3 | High |

**Urgency** (for incidents):
| Value | Label |
|-------|-------|
| 1 | Low |
| 2 | Medium |
| 3 | High |

**Example request**:

```bash
curl -X GET \
  -u "<API_KEY>:X" \
  -H "Content-Type: application/json" \
  "https://<your_domain>.freshservice.com/api/v2/tickets?per_page=30"
```

**Example response**:

```json
{
  "tickets": [
    {
      "id": 1,
      "workspace_id": 1,
      "subject": "Support Needed...",
      "description": "<div>Details about the issue...</div>",
      "description_text": "Details about the issue...",
      "type": "Incident",
      "status": 2,
      "priority": 2,
      "source": 2,
      "requester_id": 1000000001,
      "responder_id": 1000000002,
      "group_id": 1000000003,
      "department_id": null,
      "company_id": null,
      "category": "Hardware",
      "sub_category": "Laptop",
      "item_category": null,
      "impact": 2,
      "urgency": 2,
      "due_by": "2025-01-15T12:00:00Z",
      "fr_due_by": "2025-01-14T12:00:00Z",
      "is_escalated": false,
      "fr_escalated": false,
      "spam": false,
      "deleted": false,
      "email_config_id": null,
      "cc_emails": [],
      "fwd_emails": [],
      "reply_cc_emails": [],
      "to_emails": null,
      "attachments": [],
      "custom_fields": {
        "cf_employee_id": "EMP001"
      },
      "tags": ["hardware", "laptop"],
      "created_at": "2025-01-10T09:00:00Z",
      "updated_at": "2025-01-10T10:30:00Z"
    }
  ]
}
```

> The columns listed above define the **complete connector schema** for the `tickets` table.
> If additional Freshservice ticket fields are needed in the future, they must be added as new columns here so the documentation continues to reflect the full table schema.


## **Get Object Primary Keys**

There is no dedicated metadata endpoint to get the primary key for the `tickets` object.
Instead, the primary key is defined **statically** based on the resource schema.

- **Primary key for `tickets`**: `id`
  - Type: 64-bit integer
  - Property: Unique across all tickets within the Freshservice account.

The connector will:
- Read the `id` field from each ticket record returned by `GET /api/v2/tickets`.
- Use it as the immutable primary key for upserts when ingestion type is `cdc`.

Example showing primary key in response:

```json
{
  "id": 1,
  "subject": "Support Needed...",
  "status": 2,
  "created_at": "2025-01-10T09:00:00Z",
  "updated_at": "2025-01-10T10:30:00Z"
}
```


## **Object's Ingestion Type**

Supported ingestion types (framework-level definitions):
- `cdc`: Change data capture; supports upserts and/or deletes incrementally.
- `snapshot`: Full replacement snapshot; no inherent incremental support.
- `append`: Incremental but append-only (no updates/deletes).

**Planned ingestion type for `tickets`**: `cdc`

| Object | Ingestion Type | Rationale |
|--------|----------------|-----------|
| `tickets` | `cdc` | Tickets have a stable primary key `id` and an `updated_at` field that can be used as a cursor for incremental syncs. The `deleted` field indicates soft-deleted tickets. |

For `tickets`:
- **Primary key**: `id`
- **Cursor field**: `updated_at`
- **Sort order**: The API returns tickets in descending order by default. For incremental sync, use `updated_since` filter parameter.
- **Deletes**: Freshservice uses soft deletes; the `deleted` field is set to `true` for trashed tickets. Hard-deleted tickets are not retrievable.


## **Read API for Data Retrieval**

### Primary read endpoint for `tickets`

- **HTTP method**: `GET`
- **Endpoint**: `/api/v2/tickets`
- **Base URL**: `https://<your_domain>.freshservice.com`

**Query parameters** (relevant for ingestion):

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `per_page` | integer | no | 30 | Number of results per page (max 100). |
| `page` | integer | no | 1 | Page number of the results to fetch. |
| `filter` | string | no | none | Predefined filter name. Options: `new_and_my_open`, `watching`, `spam`, `deleted`. |
| `requester_id` | integer | no | none | Filter tickets by requester ID. |
| `email` | string | no | none | Filter tickets by requester email. |
| `updated_since` | string (ISO 8601 datetime) | no | none | Return tickets updated at or after this time. Used for incremental reads. |
| `type` | string | no | none | Filter by ticket type (e.g., `Incident`, `Service Request`). |
| `include` | string | no | none | Include additional information. Options: `requester`, `stats`, `department`, `problem`, `assets`, `change`, `related_tickets`, `requested_for`. Use comma-separated values for multiple includes. |
| `order_by` | string | no | `created_at` | Field to sort by. Options: `created_at`, `due_by`, `updated_at`, `status`. |
| `order_type` | string | no | `desc` | Sort direction: `asc` or `desc`. |

**Advanced filtering with `query` parameter**:

For more complex filtering, use the `query` parameter with Freshservice Query Language:

```
GET /api/v2/tickets?query="priority:2 AND status:3"
```

Query syntax:
- Use double quotes around the query string
- Logical operators: `AND`, `OR`
- Relational operators: `:` (equals), `:>` (greater than), `:<` (less than)
- URL-encode the query string

Example queries:
- Filter by status: `query="status:2"` (Open tickets)
- Filter by priority and status: `query="priority:4 AND status:2"` (Urgent and Open)
- Filter by date: `query="created_at:>'2025-01-01'"` (Tickets created after Jan 1, 2025)

**Pagination strategy**:
- Freshservice uses traditional page-based pagination with `per_page` and `page` parameters.
- The response includes the ticket count but does not include explicit pagination links.
- The connector should:
  - Request with `per_page=100` (maximum) for efficiency.
  - Continue incrementing `page` until an empty `tickets` array is returned.

**Rate Limits**:
- Rate limits vary by Freshservice plan:
  - **Starter/Growth**: TBD: Check your account's rate limit headers
  - **Pro/Enterprise**: Higher limits
- Rate limit information is returned in response headers:
  - `X-RateLimit-Total`: Total number of requests allowed per minute
  - `X-RateLimit-Remaining`: Number of requests remaining in the current window
  - `X-RateLimit-Used-CurrentRequest`: Number of API calls consumed by the current request
- When rate limited, the API returns HTTP status `429 Too Many Requests`
- Recommended: Implement exponential backoff when encountering rate limits

Example incremental read using `updated_since`:

```bash
SINCE_TS="2025-01-01T00:00:00Z"
curl -X GET \
  -u "<API_KEY>:X" \
  -H "Content-Type: application/json" \
  "https://<your_domain>.freshservice.com/api/v2/tickets?updated_since=${SINCE_TS}&per_page=100&order_by=updated_at&order_type=asc"
```

**Incremental strategy**:
- On the first run, the connector can:
  - Either perform a full historical backfill (no `updated_since`), or
  - Use a configurable `start_date` as the initial cursor.
- On subsequent runs:
  - Use the maximum `updated_at` value (minus a small lookback window, e.g., a few minutes) from the previous sync as the new `updated_since` parameter.
  - Sort by `updated_at` ascending to process records in order.

**Handling deletes**:
- Deleted tickets can be retrieved using the `filter=deleted` parameter:
  ```bash
  curl -X GET \
    -u "<API_KEY>:X" \
    "https://<your_domain>.freshservice.com/api/v2/tickets?filter=deleted&per_page=100"
  ```
- Alternatively, tickets have a `deleted` boolean field that is set to `true` when trashed.
- The connector should:
  - Periodically check the deleted tickets filter to identify soft-deleted records.
  - Mark records with `deleted=true` as deleted in downstream systems.

### View a single ticket

- **HTTP method**: `GET`
- **Endpoint**: `/api/v2/tickets/{ticket_id}`

```bash
curl -X GET \
  -u "<API_KEY>:X" \
  "https://<your_domain>.freshservice.com/api/v2/tickets/1"
```

This endpoint returns the full ticket object, useful for fetching individual ticket details.

### Retrieve ticket fields (schema discovery)

- **HTTP method**: `GET`
- **Endpoint**: `/api/v2/ticket_fields`

```bash
curl -X GET \
  -u "<API_KEY>:X" \
  "https://<your_domain>.freshservice.com/api/v2/ticket_fields"
```

This endpoint returns all ticket fields including custom fields defined in your Freshservice account.


## **Field Type Mapping**

### General mapping (Freshservice JSON → connector logical types)

| Freshservice JSON Type | Example Fields | Connector Logical Type | Notes |
|------------------------|----------------|------------------------|-------|
| integer (32/64-bit) | `id`, `requester_id`, `status`, `priority` | `long` / integer | For Spark-based connectors, prefer 64-bit integer (`LongType`). |
| string | `subject`, `description`, `type`, `category` | string | UTF-8 text. Long HTML descriptions should be supported. |
| boolean | `is_escalated`, `spam`, `deleted` | boolean | Standard true/false. |
| string (ISO 8601 datetime) | `created_at`, `updated_at`, `due_by`, `fr_due_by` | timestamp with timezone | Stored as UTC timestamps; parsing must respect ISO 8601 format. |
| object | `custom_fields` | struct (map) | Represented as a map/struct of custom field key-value pairs. |
| array | `tags`, `cc_emails`, `attachments` | array\<string\> or array\<struct\> | Arrays of strings or nested objects. |
| nullable fields | `description`, `responder_id`, `group_id` | corresponding type + null | When fields are absent or null, the connector should surface `null`, not `{}`. |

### Special behaviors and constraints

- `id` and other numeric identifiers should be stored as **64-bit integers** to avoid overflow.
- `status`, `priority`, `source`, `impact`, `urgency` are effectively enums represented as integers; the connector preserves them as integers for flexibility.
- Timestamp fields use ISO 8601 format (e.g., `"2025-01-10T09:00:00Z"`); parsing must handle timezone designators.
- `custom_fields` is a dynamic map structure whose keys and value types depend on the account's configuration; the connector should treat this as a struct/map type.
- `attachments` is an array of structured objects; each attachment has its own schema.
- Boolean fields like `deleted`, `spam`, `is_escalated` indicate ticket states that may affect downstream processing.


## **Write API**

The initial connector implementation is primarily **read-only**. However, for completeness, the Freshservice REST API supports write operations relevant to the `tickets` object.

### Create a ticket

- **HTTP method**: `POST`
- **Endpoint**: `/api/v2/tickets`

**Request body (JSON)**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `subject` | string | no | Title of the ticket (auto-generated if not provided). |
| `description` | string | no | HTML content of the ticket. |
| `requester_id` | integer | conditional | User ID of the requester. Required if `email` is not provided. |
| `email` | string | conditional | Email of the requester. Required if `requester_id` is not provided. Creates a new contact if email doesn't exist. |
| `status` | integer | yes | Status of the ticket (e.g., 2 for Open). |
| `priority` | integer | yes | Priority of the ticket (e.g., 1 for Low). |
| `source` | integer | no | Channel source (defaults to 2 for Portal). |
| `type` | string | no | Ticket type (e.g., `Incident`, `Service Request`). |
| `responder_id` | integer | no | ID of the agent to assign. |
| `group_id` | integer | no | ID of the group to assign. |
| `category` | string | no | Category of the ticket. |
| `sub_category` | string | no | Sub-category of the ticket. |
| `item_category` | string | no | Item category of the ticket. |
| `custom_fields` | object | no | Custom field key-value pairs. |
| `tags` | array | no | Tags to associate with the ticket. |
| `attachments` | array | no | File attachments (multipart form data). |

Example request:

```bash
curl -X POST \
  -u "<API_KEY>:X" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Laptop not working",
    "description": "<div>My laptop screen is blank.</div>",
    "email": "john.doe@example.com",
    "status": 2,
    "priority": 2,
    "type": "Incident",
    "category": "Hardware",
    "sub_category": "Laptop"
  }' \
  "https://<your_domain>.freshservice.com/api/v2/tickets"
```

### Update a ticket

- **HTTP method**: `PUT`
- **Endpoint**: `/api/v2/tickets/{ticket_id}`

**Commonly updated fields**:
- `subject`
- `description`
- `status`
- `priority`
- `responder_id`
- `group_id`
- `category`, `sub_category`, `item_category`
- `custom_fields`
- `tags`

Example request to update status:

```bash
curl -X PUT \
  -u "<API_KEY>:X" \
  -H "Content-Type: application/json" \
  -d '{"status": 4}' \
  "https://<your_domain>.freshservice.com/api/v2/tickets/1"
```

### Delete a ticket

- **HTTP method**: `DELETE`
- **Endpoint**: `/api/v2/tickets/{ticket_id}`

This moves the ticket to trash (soft delete). The ticket can be restored later.

```bash
curl -X DELETE \
  -u "<API_KEY>:X" \
  "https://<your_domain>.freshservice.com/api/v2/tickets/1"
```

### Restore a deleted ticket

- **HTTP method**: `PUT`
- **Endpoint**: `/api/v2/tickets/{ticket_id}/restore`

```bash
curl -X PUT \
  -u "<API_KEY>:X" \
  "https://<your_domain>.freshservice.com/api/v2/tickets/1/restore"
```

**Validation / read-after-write**:
- The connector (or user) can validate writes by:
  - Reading back the updated ticket via `GET /api/v2/tickets/{ticket_id}`, or
  - Letting the next incremental read (using `updated_since`) pick up the change.


## **Known Quirks & Edge Cases**

- **Workspace support**:
  - The `workspace_id` field is only present for accounts with workspaces enabled.
  - For single-workspace accounts, this field may be null or absent.

- **Custom fields**:
  - Custom fields are account-specific and their schema varies.
  - Use `GET /api/v2/ticket_fields` to discover available custom fields and their types.
  - Custom field keys in the response are prefixed with `cf_` (e.g., `cf_employee_id`).

- **Deleted tickets**:
  - Deleted tickets are soft-deleted (moved to trash) and can be restored.
  - To retrieve deleted tickets, use `filter=deleted` parameter.
  - The `deleted` boolean field on a ticket indicates its trash status.

- **Rate limiting**:
  - Rate limits vary by subscription plan.
  - Always check `X-RateLimit-Remaining` header to avoid hitting limits.
  - Implement exponential backoff when receiving 429 responses.

- **Pagination limits**:
  - Maximum of 100 records per page with `per_page=100`.
  - Some filtered queries may have additional result limits (e.g., query filter may return max 30 days of data by default).

- **Description vs description_text**:
  - `description` contains HTML-formatted content.
  - `description_text` contains the plain text version.
  - Both fields may be present in responses.

- **Ticket types**:
  - Default types are `Incident` and `Service Request`.
  - Additional custom types can be configured in Freshservice.

- **SLA and escalation**:
  - `is_escalated` and `fr_escalated` flags indicate SLA breach status.
  - `due_by` and `fr_due_by` timestamps are computed based on SLA policies.


## **Research Log**

| Source Type | URL | Accessed (UTC) | Confidence | What it confirmed |
|------------|-----|----------------|------------|-------------------|
| Official Docs | https://api.freshservice.com/#ticket_attributes | 2025-12-23 | High | Ticket object attributes, data types, and enumerated values for status, priority, source. |
| Official Docs | https://api.freshservice.com/ | 2025-12-23 | High | API endpoint structure, authentication method (Basic Auth with API key), and general API behavior. |
| Official Support | https://support.freshservice.com/support/solutions/articles/50000000294 | 2025-12-23 | High | How to retrieve ticket fields using API, including custom fields. |
| Official Docs | https://developers.freshworks.com/api-sdk/freshservice/tickets.html | 2025-12-23 | High | Ticket SDK documentation with attribute descriptions and examples. |
| Web Search | Various search results | 2025-12-23 | Medium | Confirmed ticket attributes, pagination, and filtering options. |


## **Sources and References**

- **Official Freshservice REST API documentation** (highest confidence)
  - `https://api.freshservice.com/`
  - `https://api.freshservice.com/#ticket_attributes`
  - `https://api.freshservice.com/#list_all_tickets`
  - `https://api.freshservice.com/#view_a_ticket`
  - `https://api.freshservice.com/#create_a_ticket`
  - `https://api.freshservice.com/#update_a_ticket`
  - `https://api.freshservice.com/#delete_a_ticket`
  - `https://api.freshservice.com/#restore_a_ticket`
  - `https://api.freshservice.com/#filter_tickets`

- **Freshworks Developer Documentation** (high confidence)
  - `https://developers.freshworks.com/api-sdk/freshservice/tickets.html`

- **Freshservice Support Documentation** (high confidence)
  - `https://support.freshservice.com/support/solutions/articles/50000000294` (Get ticket fields via API)

When conflicts arise, **official Freshservice API documentation** is treated as the source of truth.


## **Acceptance Checklist**

- [x] All required headings present and in order.
- [x] Every field in the tickets schema is listed (no omissions).
- [x] Exactly one authentication method is documented (Basic Auth with API Key).
- [x] Endpoints include params, examples, and pagination details.
- [x] Incremental strategy defines cursor (`updated_at`), order, lookback, and delete handling.
- [x] Research Log completed; Sources include full URLs.
- [x] No unverifiable claims; rate limit details noted as plan-dependent.

