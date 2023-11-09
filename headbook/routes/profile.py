from datetime import date
from flask import (
    request,
    render_template,
)
from flask_login import current_user, login_required
from headbook import app
from headbook.forms.profile_form import ProfileForm
from headbook.modules.utils import debug
from headbook.modules.hashing import hash_password


@app.route("/profile/", methods=["GET", "POST", "PUT"])
@login_required
def my_profile():
    """Display or edit user's profile info"""
    debug("/profile/ – current user:", current_user, request.host_url)

    form = ProfileForm()
    if form.is_submitted():
        debug(
            f'Received form:\n    {form.data}\n    {f"INVALID: {form.errors}" if not form.validate() else "ok"}'
        )
        if form.validate():
            if form.password.data:  # change password if user set it
                current_user.password = hash_password(form.password.data)
            if form.birthdate.data:  # change birthday if set
                current_user.birthdate = form.birthdate.data.isoformat()
            # TODO: do we need additional validation for these?
            current_user.color = form.color.data
            current_user.picture_url = form.picture_url.data
            current_user.about = form.about.data
            current_user.save()
        else:
            pass  # The profile.html template will display any errors in form.errors
    else:  # fill in the form with the user's info
        form.username.data = current_user.username
        form.password.data = ""
        form.password_again.data = ""
        # only set this if we have a valid date
        form.birthdate.data = current_user.get("birthdate") and date.fromisoformat(
            current_user.get("birthdate")
        )
        form.color.data = current_user.get("color", "")
        form.picture_url.data = current_user.get("picture_url", "")
        form.about.data = current_user.get("about", "")

    return render_template("profile.html", form=form, user=current_user)
