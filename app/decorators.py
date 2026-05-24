from functools import wraps

from flask import abort
from flask_login import current_user, login_required


def role_required(*role_names):
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped_view(*args, **kwargs):
            if not current_user.role or current_user.role.name not in role_names:
                abort(403)
            return view(*args, **kwargs)

        return wrapped_view

    return decorator
