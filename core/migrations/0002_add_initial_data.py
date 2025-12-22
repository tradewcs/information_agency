from django.db import migrations
from django.contrib.auth.hashers import make_password


def create_initial_data(apps, schema_editor):
    Publisher = apps.get_model("core", "Publisher")
    Topik = apps.get_model("core", "Topik")

    topics = [
        "Politics",
        "Economy",
        "Technology",
        "Science",
        "Health",
        "Sports",
        "Culture",
        "Entertainment",
        "World",
        "Local",
        "Business",
        "Education",
        "Environment",
        "Travel",
        "Lifestyle",
        "Opinion",
        "Law",
        "Art",
        "Food",
        "Media",
    ]

    for name in topics:
        Topik.objects.get_or_create(name=name)

    publishers = [
        {"username": "alice", "email": "alice@example.com", "first_name": "Alice", "last_name": "Smith", "years": 3, "password": "pass1234"},
        {"username": "bob", "email": "bob@example.com", "first_name": "Bob", "last_name": "Jenkins", "years": 5, "password": "pass1234"},
        {"username": "carol", "email": "carol@example.com", "first_name": "Carol", "last_name": "Olson", "years": 2, "password": "pass1234"},
        {"username": "dave", "email": "dave@example.com", "first_name": "Dave", "last_name": "Brown", "years": 7, "password": "pass1234"},
        {"username": "eve", "email": "eve@example.com", "first_name": "Eve", "last_name": "Davis", "years": 1, "password": "pass1234"},
    ]

    for p in publishers:
        obj, created = Publisher.objects.get_or_create(
            username=p["username"],
            defaults={
                "email": p["email"],
                "first_name": p["first_name"],
                "last_name": p["last_name"],
                "years_of_experience": p["years"],
            },
        )

        obj.password = make_password(p["password"])
        obj.save()


def remove_initial_data(apps, schema_editor):
    Publisher = apps.get_model("core", "Publisher")
    Topik = apps.get_model("core", "Topik")

    topics = [
        "Politics",
        "Economy",
        "Technology",
        "Science",
        "Health",
        "Sports",
        "Culture",
        "Entertainment",
        "World",
        "Local",
        "Business",
        "Education",
        "Environment",
        "Travel",
        "Lifestyle",
        "Opinion",
        "Law",
        "Art",
        "Food",
        "Media",
    ]

    for name in topics:
        Topik.objects.filter(name=name).delete()

    usernames = ["alice", "bob", "carol", "dave", "eve"]
    for username in usernames:
        Publisher.objects.filter(username=username).delete()


class Migration(migrations.Migration):

    dependencies = [("core", "0001_initial")]

    operations = [migrations.RunPython(create_initial_data, reverse_code=remove_initial_data)]
