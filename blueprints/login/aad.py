from flask import Flask, url_for
from flask.sessions import SessionMixin
from typing import Callable, List

no_logged_message = "You are not logged in. Redirecting in 3 seconds."


def authorisation(app: Flask, session: SessionMixin, excluded: List[str]):
    """Creat the authorisation for all the view"""
    for view_func in app.view_functions:
        if view_func not in excluded:
            print(view_func)
            app.view_functions[view_func] = _authorize_view(
                app.view_functions[view_func], session
            )

    return app


def is_user_authenticate(session: SessionMixin) -> bool:
    """Check if the user is connected by looking the session"""
    # Check if the user is in the session
    return "user" in session


def _authorize_view(func: Callable, session: SessionMixin):
    """Require Special Access for the given view function on top of the login."""

    def check_authorization(*args, **kwargs):
        if is_user_authenticate(session=session):
            return func(*args, **kwargs)

        response = no_logged_message, {"Refresh": f"3; url={url_for('login.landing')}"}
        return response

    return check_authorization
