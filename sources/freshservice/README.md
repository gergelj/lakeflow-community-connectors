# Lakeflow Freshservice Community Connector

This documentation provides setup instructions and reference information for the Freshservice source connector.

## Prerequisites

- A Freshservice account with at least **Agent** role permissions
- An API key generated from your Freshservice account
- Your Freshservice domain (e.g., `acme` for `acme.freshservice.com`)

## Setup

### Required Connection Parameters

To configure the connector, provide the following parameters in your connector options:

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `api_key` | string | Yes | API key for Freshservice REST API authentication. Uses Basic Authentication with the key as username and 'X' as password. | `your_api_key_here` |
| `domain` | string | Yes | Your Freshservice subdomain. Do not include the full URL or '.freshservice.com' suffix. | `acme` |
| `externalOptionsAllowList` | string | Yes | Comma-separated list of table-specific options that can be passed through. | `per_page,max_pages_per_batch,lookback_seconds,start_date,max_parents,max_parents_per_type` |

### External Options Allowlist

The following table-specific options are supported and must be included in `externalOptionsAllowList`:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `per_page` | integer | 100 | Number of records per API page (max 100) |
| `max_pages_per_batch` | integer | 100 | Maximum pages to fetch per batch |
| `lookback_seconds` | integer | 300 | Lookback window for cursor calculation to handle late-arriving updates |
| `start_date` | string | - | ISO 8601 datetime for initial cursor (e.g., `2025-01-01T00:00:00Z`) |
| `max_parents` | integer | 1000 | Maximum parent records to iterate for child objects (time_entries, conversations, solutions) |
| `max_parents_per_type` | integer | 500 | Maximum parent records per type for multi-parent child objects (tasks) |

### Obtaining Your API Key

1. Log in to your Freshservice account
2. Click on your profile picture in the top-right corner
3. Navigate to **Profile Settings**
4. Your API key will be displayed under the "Your API Key" section
5. Copy the API key and store it securely

**Note**: The API key inherits the permissions of the user account it belongs to. For read-only access, the user needs at least the **Agent** role with appropriate viewing permissions.

### Create a Unity Catalog Connection

A Unity Catalog connection for this connector can be created in two ways via the UI:

1. Follow the Lakeflow Community Connector UI flow from the "Add Data" page
2. Select any existing Lakeflow Community Connector connection for Freshservice or create a new one
3. Set `externalOptionsAllowList` to: `per_page,max_pages_per_batch,lookback_seconds,start_date,max_parents,max_parents_per_type`

The connection can also be created using the standard Unity Catalog API.

## Supported Objects

The connector supports 28 Freshservice objects organized by category.

### Core ITSM Objects

| Object Name | Primary Key | Ingestion Type | Cursor Field | Description |
|-------------|-------------|----------------|--------------|-------------|
| `tickets` | `id` | CDC with Deletes | `updated_at` | Support tickets (incidents and service requests). Supports delete synchronization via `deleted` flag. |
| `problems` | `id` | Incremental (CDC) | `updated_at` | Problem records linked to incidents |
| `changes` | `id` | Incremental (CDC) | `updated_at` | Change management requests |
| `releases` | `id` | Incremental (CDC) | `updated_at` | Release management records |

### User & Organization Objects

| Object Name | Primary Key | Ingestion Type | Cursor Field | Description |
|-------------|-------------|----------------|--------------|-------------|
| `agents` | `id` | Incremental (CDC) | `updated_at` | Support agents handling tickets |
| `requesters` | `id` | Incremental (CDC) | `updated_at` | End-users who raise tickets |
| `groups` | `id` | Snapshot | - | Agent groups for ticket assignment |
| `departments` | `id` | Snapshot | - | Organizational departments |
| `roles` | `id` | Snapshot | - | Agent roles with permissions |

### Asset Management Objects

| Object Name | Primary Key | Ingestion Type | Cursor Field | Description |
|-------------|-------------|----------------|--------------|-------------|
| `assets` | `id` | Incremental (CDC) | `updated_at` | IT assets (hardware, software, etc.) |
| `software` | `id` | Snapshot | - | Software installations/applications |
| `products` | `id` | Snapshot | - | Product catalog |
| `vendors` | `id` | Snapshot | - | Vendor information |
| `contracts` | `id` | Snapshot | - | Contracts with vendors |
| `purchase_orders` | `id` | Incremental (CDC) | `updated_at` | Purchase orders |

### Service Catalog & Knowledge Base Objects

| Object Name | Primary Key | Ingestion Type | Cursor Field | Description |
|-------------|-------------|----------------|--------------|-------------|
| `service_catalog_items` | `id` | Snapshot | - | Service items offered to users |
| `solution_categories` | `id` | Snapshot | - | Knowledge base categories |
| `solution_folders` | `id` | Snapshot | - | Knowledge base folders |
| `solutions` | `id` | Incremental (CDC) | `updated_at` | Knowledge base articles (child of solution_folders) |
| `canned_responses` | `id` | Snapshot | - | Pre-defined response templates |

### Configuration Objects

| Object Name | Primary Key | Ingestion Type | Cursor Field | Description |
|-------------|-------------|----------------|--------------|-------------|
| `locations` | `id` | Snapshot | - | Physical office locations |
| `sla_policies` | `id` | Snapshot | - | SLA policy definitions |
| `business_hours` | `id` | Snapshot | - | Business hours configuration |
| `announcements` | `id` | Snapshot | - | Broadcast messages to users |
| `ticket_fields` | `id` | Snapshot | - | Ticket field definitions |

### Child Objects

These objects are fetched by iterating over parent records:

| Object Name | Primary Key | Parent Object(s) | Description |
|-------------|-------------|------------------|-------------|
| `time_entries` | `id`, `ticket_id` | `tickets` | Time logs for tickets |
| `conversations` | `id`, `ticket_id` | `tickets` | Ticket conversations (notes/replies) |
| `tasks` | `id`, `parent_id`, `parent_type` | `tickets`, `problems`, `changes`, `releases` | Tasks associated with parent objects |
| `solutions` | `id` | `solution_folders` | Knowledge base articles |

**Note**: Child objects require iterating over parent records to fetch data. Use `max_parents` or `max_parents_per_type` options to limit API usage.

### Ingestion Types Explained

- **CDC with Deletes**: The `tickets` object supports both incremental loading and delete synchronization. Deleted tickets are fetched using the `filter=deleted` parameter and can be synchronized to your target table.
- **Incremental (CDC)**: Objects support incremental loading using the `updated_at` field as a cursor. Only records modified since the last sync are fetched.
- **Snapshot**: Objects are fully refreshed on each sync. They typically contain smaller datasets or don't support incremental filtering.
- **Child Objects**: Objects like `time_entries`, `conversations`, `tasks`, and `solutions` are fetched by iterating over parent records.

### Special Columns

- **`custom_fields`**: Many objects include a `custom_fields` column containing a map of custom field key-value pairs. Custom field keys are prefixed with `cf_` (e.g., `cf_employee_id`).
- **`deleted`**: The `tickets` and `sla_policies` objects include a `deleted` boolean field for soft-deleted records.
- **`active`**: The `agents` and `requesters` objects include an `active` boolean field indicating if the user is active.

## Data Type Mapping

| Freshservice Type | Databricks Type | Notes |
|-------------------|-----------------|-------|
| integer | Long | 64-bit integers |
| string | String | UTF-8 text |
| boolean | Boolean | true/false values |
| datetime (ISO 8601) | String | Stored as ISO 8601 formatted strings |
| date | String | YYYY-MM-DD format |
| object | Struct / Map | Nested structures |
| array | Array | Array of elements |
| number (decimal) | Double | Decimal numbers |

## How to Run

### Step 1: Clone/Copy the Source Connector Code

Follow the Lakeflow Community Connector UI, which will guide you through setting up a pipeline using the selected source connector code.

### Step 2: Configure Your Pipeline

1. Update the `pipeline_spec` in the main pipeline file (e.g., `ingest.py`).
2. Configure the objects you want to ingest:

```json
{
  "pipeline_spec": {
    "connection_name": "your_freshservice_connection",
    "object": [
      {
        "table": {
          "source_table": "tickets"
        }
      },
      {
        "table": {
          "source_table": "agents"
        }
      },
      {
        "table": {
          "source_table": "assets"
        }
      }
    ]
  }
}
```

3. For child objects, you can optionally limit the number of parent records to iterate over:

```json
{
  "pipeline_spec": {
    "connection_name": "your_freshservice_connection",
    "object": [
      {
        "table": {
          "source_table": "time_entries",
          "max_parents": "500"
        }
      },
      {
        "table": {
          "source_table": "conversations",
          "max_parents": "500"
        }
      },
      {
        "table": {
          "source_table": "tasks",
          "max_parents_per_type": "200"
        }
      },
      {
        "table": {
          "source_table": "solutions",
          "max_parents": "100"
        }
      }
    ]
  }
}
```

4. For incremental objects, you can set a custom start date:

```json
{
  "pipeline_spec": {
    "connection_name": "your_freshservice_connection",
    "object": [
      {
        "table": {
          "source_table": "tickets",
          "start_date": "2024-01-01T00:00:00Z"
        }
      }
    ]
  }
}
```

5. (Optional) Customize the source connector code if needed for special use cases.

### Step 3: Run and Schedule the Pipeline

#### Best Practices

- **Start Small**: Begin by syncing a subset of objects (e.g., `tickets`, `agents`) to test your pipeline before adding more objects
- **Use Incremental Sync**: Objects with CDC ingestion type (like `tickets`, `assets`, `changes`) automatically use incremental loading, reducing API calls and improving performance
- **Set Appropriate Schedules**: Balance data freshness requirements with API usage limits. Consider scheduling:
  - High-volume objects (tickets, assets): Every 15-30 minutes
  - Configuration objects (roles, sla_policies): Daily
- **Monitor Rate Limits**: Freshservice rate limits vary by subscription plan. The connector handles rate limiting automatically with retry logic, but scheduling multiple pipelines simultaneously may increase API usage
- **Limit Child Object Parents**: Use `max_parents` and `max_parents_per_type` options to control API usage when syncing child objects

#### Troubleshooting

**Common Issues:**

| Issue | Cause | Solution |
|-------|-------|----------|
| Authentication errors | Invalid or expired API key | Regenerate the API key from Freshservice Profile Settings |
| 403 Forbidden | Insufficient permissions | Ensure the API key owner has Agent role with appropriate viewing permissions |
| 429 Too Many Requests | Rate limit exceeded | The connector handles this automatically; consider reducing sync frequency if persistent |
| Empty data for some objects | No data in source or insufficient permissions | Verify data exists in Freshservice and user has access to the relevant modules |
| Missing custom fields | Custom fields not configured | Ensure custom fields are created in Freshservice admin settings |
| Child objects slow to sync | Too many parent records | Use `max_parents` or `max_parents_per_type` to limit iteration |
| Missing deleted tickets | Delete sync not enabled | Ensure `tickets` table is configured; deleted records are fetched automatically |

## References

- [Freshservice REST API Documentation](https://api.freshservice.com/)
- [Freshworks Developer Documentation](https://developers.freshworks.com/)
- [Freshservice Support Center](https://support.freshservice.com/)
