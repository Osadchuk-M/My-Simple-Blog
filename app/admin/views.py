from flask import request, render_template, flash
from flask_login import login_required
from . import admin
from .forms import EditProfileForm
from ..models import User


@admin.route('/profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
def profile(user_id):
    user = User.query.get_or_404(user_id)
    form = EditProfileForm()
    if form.validate_on_submit():
        user.update_from_form(form)
        flash('Your profile has been updated.')
    form.fill_the_form(user)
    return render_template('admin/profile.html', form=form)
