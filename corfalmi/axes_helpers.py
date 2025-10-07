def never_lockout_superusers(user):
    return user.is_superuser