from __future__ import annotations

from datetime import timedelta

DOMAIN = "tap"

PLATFORMS = ["sensor"]

CONF_API_BASE_URL = "api_base_url"
CONF_COGNITO_DOMAIN = "cognito_domain"
CONF_CLIENT_ID = "client_id"
CONF_SCOPES = "scopes"

DEFAULT_SCOPES = "openid email profile"
DEFAULT_SCAN_INTERVAL = timedelta(seconds=60)

# Production defaults (Tap cloud)
PROD_API_BASE_URL = "https://pusyi0t8ik.execute-api.ap-southeast-2.amazonaws.com/prod"
PROD_COGNITO_DOMAIN = "https://auth.tapprfid.com"
PROD_CLIENT_ID = "324uq6sglq2rmkfh4c055bngfe"
PROD_SCOPES = DEFAULT_SCOPES

API_PATH_SUMMARY = "/ha/v2/summary"
API_PATH_TASKS = "/ha/v2/tasks"
API_PATH_EVENTS = "/ha/v2/events"
API_PATH_LOGS = "/ha/v2/logs"
API_PATH_COMPLETE_TASK = "/ha/v2/actions/complete-task"
API_PATH_REOPEN_TASK = "/ha/v2/actions/reopen-task"
API_PATH_ADD_LOG_ENTRY = "/ha/v2/actions/add-log-entry"

SERVICE_COMPLETE_TASK = "complete_task"
SERVICE_REOPEN_TASK = "reopen_task"
SERVICE_ADD_LOG_ENTRY = "add_log_entry"

ATTR_TASK_ID = "task_id"
ATTR_LOG_ID = "log_id"
ATTR_NOTE = "note"

DATA_API = "api"
DATA_COORDINATOR = "coordinator"
DATA_LISTENER_UNSUB = "listener_unsub"
