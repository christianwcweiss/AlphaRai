########################################################################################################################
# IDs
########################################################################################################################
from quant_core.enums.platform import Platform
from quant_core.enums.prop_firm import PropFirm

_IDS_PAGE_PREFIX = "accounts-overview"

# Page
LOADING_PAGE_ID = f"{_IDS_PAGE_PREFIX}-loading-accounts"
OPEN_ADD_ACCOUNT_MODAL_ID = f"{_IDS_PAGE_PREFIX}-open-add-account-modal"
CONTENT_ROWS = f"{_IDS_PAGE_PREFIX}-content-rows"
PAGE_INIT = f"{_IDS_PAGE_PREFIX}-page-init"

# Modals
ADD_ACCOUNT_MODAL_ID = f"{_IDS_PAGE_PREFIX}-add-account-modal"
INPUT_ACCOUNT_NAME_ID = f"{_IDS_PAGE_PREFIX}-input-account-name"
INPUT_ACCOUNT_SECRET_ID = f"{_IDS_PAGE_PREFIX}-input-account-secret"
INPUT_PLATFORM_ID = f"{_IDS_PAGE_PREFIX}-input-platform"
INPUT_PROP_FIRM = f"{_IDS_PAGE_PREFIX}-input-prop-firm"
ADD_ACCOUNT_CONFIRM_BUTTON_ID = f"{_IDS_PAGE_PREFIX}-confirm-add-account"
ADD_ACCOUNT_CANCEL_BUTTON_ID = f"{_IDS_PAGE_PREFIX}-cancel-add-account"

# Delete Account Modal
DELETE_ACCOUNT_MODAL_ID = f"{_IDS_PAGE_PREFIX}-delete-account-modal"
DELETE_ACCOUNT_MODAL_CONFIRM_BUTTON_ID = f"{_IDS_PAGE_PREFIX}-delete-account-confirm-button"
DELETE_ACCOUNT_MODAL_CANCEL_BUTTON_ID = f"{_IDS_PAGE_PREFIX}-delete-account-cancel-button"

########################################################################################################################
# Labels and Titles
########################################################################################################################

# Page Buttons
ADD_ACCOUNT_BUTTON_LABEL = "Add a new Account"

# Add Account Modal
ADD_ACCOUNT_MODAL_TITLE = "Add Account"
INPUT_ACCOUNT_NAME_LABEL = "Friendly Name"
INPUT_ACCOUNT_SECRET_LABEL = "AWS Secret Name"
INPUT_PLATFORM_LABEL = "Select Platform"
INPUT_PROP_FIRM_LABEL = "Select Prop Firm"
ADD_ACCOUNT_CONFIRM_BUTTON_LABEL = "Confirm Account"
ADD_ACCOUNT_CANCEL_BUTTON_LABEL = "Cancel"

# Delete Account Modal
DELETE_ACCOUNT_MODAL_TITLE = "Confirm Account Deletion"
DELETE_ACCOUNT_MODAL_BODY = "Are you sure you want to delete this account? This action cannot be undone."
DELETE_ACCOUNT_MODAL_CONFIRM_BUTTON_LABEL = "Delete Account"
DELETE_ACCOUNT_MODAL_CANCEL_BUTTON_LABEL = "Cancel"

########################################################################################################################
# Store
########################################################################################################################
PENDING_DELETE_UID_ID = f"{_IDS_PAGE_PREFIX}-pending-delete-uid"

########################################################################################################################
# Options
########################################################################################################################
PLATFORM_OPTIONS = [{"label": platform.name.title(), "value": platform.value} for platform in Platform]
PROP_FIRM_OPTIONS = [{"label": firm.value, "value": firm.value} for firm in PropFirm]

########################################################################################################################
# Tooltip Text
########################################################################################################################
