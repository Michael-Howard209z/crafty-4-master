import logging
import json
from jsonschema import validate
from jsonschema.exceptions import ValidationError

from app.classes.models.crafty_permissions import PermissionsCrafty
from app.classes.web.base_api_handler import BaseApiHandler

logger = logging.getLogger(__name__)

register_schema = {
    "type": "object",
    "required": ["username", "password", "email"],
    "additionalProperties": False,
    "properties": {
        "username": {
            "type": "string",
            "minLength": 3,
            "maxLength": 20,
            "pattern": r"^[a-zA-Z0-9_]+$",
            "error": "registerUsername",
        },
        "password": {
            "type": "string",
            "minLength": 6,
            "error": "registerPassword",
        },
        "email": {
            "type": "string",
            "format": "email",
            "error": "registerEmail",
        },
    },
}


class ApiAuthRegisterHandler(BaseApiHandler):
    def post(self):
        reg_enabled = self.helper.get_setting("allow_registration")
        if not reg_enabled:
            return self.finish_json(
                403,
                {
                    "status": "error",
                    "error": "REGISTRATION_DISABLED",
                    "error_data": "Registration is disabled",
                },
            )

        try:
            data = json.loads(self.request.body)
        except json.decoder.JSONDecodeError as e:
            return self.finish_json(
                400, {"status": "error", "error": "INVALID_JSON", "error_data": str(e)}
            )

        try:
            validate(data, register_schema)
        except ValidationError as why:
            offending_key = why.path[0] if why.path else None
            err = why.schema.get("error", "additionalProperties")
            return self.finish_json(
                400,
                {
                    "status": "error",
                    "error": "INVALID_JSON_SCHEMA",
                    "error_data": f"{offending_key} {err}",
                },
            )

        username = data["username"].lower().strip()
        password = data["password"]
        email = data["email"].strip()

        if username in ["system", "admin", "anti-lockout-user", ""]:
            return self.finish_json(
                400,
                {"status": "error", "error": "INVALID_USERNAME"},
            )

        if self.controller.users.get_id_by_name(username) is not None:
            return self.finish_json(
                400,
                {"status": "error", "error": "USER_EXISTS"},
            )

        user_id = self.controller.users.add_user(
            username=username,
            manager=None,
            password=password,
            email=email,
            enabled=True,
            superuser=False,
            theme="default",
            max_ram_gb=4.0,
        )

        PermissionsCrafty.add_or_update_user(
            user_id,
            permissions_mask="100",
            limit_server_creation=-1,
            limit_user_creation=0,
            limit_role_creation=0,
        )

        logger.info(f"New user registered: {username} (ID: {user_id})")

        return self.finish_json(
            201,
            {"status": "ok", "data": {"user_id": str(user_id)}},
        )
