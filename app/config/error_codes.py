# SUPABASE AUTH ERROR CODES
AUTH_ERROR_MAP = {
    # Authentication
    "invalid_credentials": (401, "invalid_credentials"),
    "user_not_found": (401, "user_not_found"),
    "email_not_confirmed": (403, "email_not_confirmed"),
    "user_banned": (403, "user_banned"),

    # Validation
    "validation_failed": (400, "validation_failed"),
    "email_address_invalid": (400, "email_address_invalid"),
    "weak_password": (400, "weak_password"),
    "captcha_failed": (400, "captcha_failed"),

    # Conflicts
    "email_exists": (409, "email_exists"),
    "user_already_exists": (409, "user_already_exists"),

    # Configuration
    "signup_disabled": (403, "signup_disabled"),
    "email_provider_disabled": (403, "email_provider_disabled"),
    "email_address_not_authorized": (403, "email_address_not_authorized"),

    # Rate limiting
    "over_request_rate_limit": (429, "over_request_rate_limit"),
    "over_email_send_rate_limit": (429, "over_email_send_rate_limit"),

    # Sessions
    "session_expired": (401, "session_expired"),
    "session_not_found": (401, "session_not_found"),
    "refresh_token_not_found": (401, "refresh_token_not_found"),
    "refresh_token_already_used": (401, "refresh_token_already_used"),

    # JWT
    "bad_jwt": (401, "bad_jwt"),
    "no_authorization": (401, "no_authorization"),

    # Server
    "request_timeout": (504, "request_timeout"),
    "unexpected_failure": (500, "unexpected_failure"),
}