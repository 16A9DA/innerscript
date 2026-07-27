from django.db import migrations

# allauth was replaced by WorkOS AuthKit; these tables are no longer
# Django-managed but their FK constraints on auth_user still exist in
# dev SQLite databases created before the switch, breaking user delete
# once deferred FK checks run at commit.
TABLES = [
    "account_emailconfirmation",
    "account_emailaddress",
    "socialaccount_socialtoken",
    "socialaccount_socialapp_sites",
    "socialaccount_socialaccount",
    "socialaccount_socialapp",
]


class Migration(migrations.Migration):
    dependencies = [("accounts", "0007_profile_site_role")]

    operations = [
        migrations.RunSQL(
            sql=[f'DROP TABLE IF EXISTS "{t}"' for t in TABLES],
            reverse_sql=migrations.RunSQL.noop,
        )
    ]
