from flask import abort, redirect, url_for, request
from flask_admin.contrib.sqla import ModelView
from flask_security import current_user
from flask_security.utils import hash_password


class AuthModelView(ModelView):

    def is_accessible(self):
        return current_user.is_active and current_user.is_authenticated and current_user.has_role('administrator')

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                abort(403)
            else:
                return redirect(url_for('security.login', next=request.url))

    can_edit = False
    edit_modal = True
    can_create = True
    create_modal = True
    can_export = False
    can_delete = True

    can_view_details = False
    column_display_pk = True


class UserView(AuthModelView):
    column_list = ['id', 'username', 'email', 'phone', 'roles', 'active']
    column_editable_list = ['email', 'phone', 'roles', 'active']

    def create_model(self, form):
        form.password.data = hash_password(form.password.data)
        return super(AuthModelView, self).create_model(form)


class RoleView(AuthModelView):
    column_editable_list = ['name', 'description']
