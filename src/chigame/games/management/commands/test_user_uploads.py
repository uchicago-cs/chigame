from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction

from chigame.games.models import Category, Game, Mechanic

User = get_user_model()


class Command(BaseCommand):
    help = "Creates test user-uploaded Twine games to verify upload functionality"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        # NOTE: This test only covers Twine file uploads.
        # Embedded game functionality is in a separate PR that hasn't been merged yet.

        # Create test user if doesn't exist
        test_user, created = User.objects.get_or_create(
            email="testuploader@example.com", defaults={"username": "testuploader", "name": "Test Uploader"}
        )
        if created:
            test_user.set_password("testpass123")
            test_user.save()
            self.stdout.write(f"Created test user: {test_user.email}")

        # Create categories for testing
        story_category = Category.objects.get_or_create(name="Storytelling")[0]
        user_created_category = Category.objects.get_or_create(name="User Created")[0]

        # Create mechanics for testing
        story_mechanic = Mechanic.objects.get_or_create(name="Storytelling")[0]
        choice_mechanic = Mechanic.objects.get_or_create(name="Player Choice")[0]

        # Test 1: Simple Twine game upload
        simple_twine_content = """
        <!DOCTYPE html>
        <html>
        <head><title>Simple Test Story</title></head>
        <body>
        <h1>The Adventure Begins</h1>
        <p>You are at a crossroads. What do you do?</p>
        <p><a href="#left">Go left</a> | <a href="#right">Go right</a></p>

        <div id="left" style="display:none;">
        <h2>Left Path</h2>
        <p>You chose the left path and found treasure!</p>
        <p><strong>THE END</strong></p>
        </div>

        <div id="right" style="display:none;">
        <h2>Right Path</h2>
        <p>You chose the right path and met a friendly dragon!</p>
        <p><strong>THE END</strong></p>
        </div>

        <script>
        document.addEventListener('click', function(e) {
            if (e.target.tagName === 'A' && e.target.getAttribute('href').startsWith('#')) {
                e.preventDefault();
                var target = document.querySelector(e.target.getAttribute('href'));
                if (target) {
                    document.body.innerHTML = target.innerHTML;
                }
            }
        });
        </script>
        </body>
        </html>
        """

        simple_twine_game, created = Game.objects.get_or_create(
            name="Test Simple Twine Story",
            defaults={
                "description": "A simple test Twine story to verify file upload functionality works correctly.",
                "min_players": 1,
                "max_players": 1,
                "complexity": 1.5,
                "expected_playtime": 5,
                "year_published": 2024,
                "image": "/static/images/no_picture_available.png",
            },
        )

        if created:
            # Create and save the Twine file
            fake_file = ContentFile(simple_twine_content.encode("utf-8"), name="simple_test_story.html")
            simple_twine_game.twine_file.save("simple_test_story.html", fake_file, save=False)
            simple_twine_game.save()

            simple_twine_game.categories.add(user_created_category, story_category)
            simple_twine_game.mechanics.add(story_mechanic, choice_mechanic)
            simple_twine_game.users.add(test_user)
            self.stdout.write(f" Created simple Twine game: {simple_twine_game.name}")

        # Test 2: More complex Twine game upload
        complex_twine_content = """
        <!DOCTYPE html>
        <html>
        <head><title>Complex Test Story</title></head>
        <body>
        <div id="story">
        <h1>The Mystery House</h1>
        <p>You enter a mysterious house. The door slams shut behind you.</p>
        <p>What do you examine first?</p>
        <p>
        <a href="#fireplace">The fireplace</a> |
        <a href="#bookshelf">The bookshelf</a> |
        <a href="#staircase">The staircase</a>
        </p>
        </div>

        <div id="fireplace" style="display:none;">
        <h2>The Fireplace</h2>
        <p>You examine the cold fireplace and find a hidden key!</p>
        <p><a href="#upstairs">Use the key to go upstairs</a></p>
        </div>

        <div id="bookshelf" style="display:none;">
        <h2>The Bookshelf</h2>
        <p>You pull a mysterious book and reveal a secret passage!</p>
        <p><a href="#secret">Enter the secret passage</a></p>
        </div>

        <div id="staircase" style="display:none;">
        <h2>The Staircase</h2>
        <p>The stairs creak ominously. You need a key to proceed.</p>
        <p><a href="#story">Go back and look for a key</a></p>
        </div>

        <div id="upstairs" style="display:none;">
        <h2>Upstairs</h2>
        <p>You unlock the upstairs door and find the treasure!</p>
        <p><strong>VICTORY! You solved the mystery!</strong></p>
        </div>

        <div id="secret" style="display:none;">
        <h2>Secret Passage</h2>
        <p>The secret passage leads to an underground chamber with ancient scrolls!</p>
        <p><strong>DISCOVERY! You found the hidden knowledge!</strong></p>
        </div>

        <script>
        document.addEventListener('click', function(e) {
            if (e.target.tagName === 'A' && e.target.getAttribute('href').startsWith('#')) {
                e.preventDefault();
                var target = document.querySelector(e.target.getAttribute('href'));
                if (target) {
                    document.body.innerHTML = target.innerHTML;
                }
            }
        });
        </script>
        </body>
        </html>
        """

        complex_twine_game, created = Game.objects.get_or_create(
            name="Test Complex Twine Mystery",
            defaults={
                "description": "A more complex test Twine game with multiple paths.",
                "min_players": 1,
                "max_players": 1,
                "complexity": 2.5,
                "expected_playtime": 10,
                "year_published": 2024,
                "image": "/static/images/no_picture_available.png",
            },
        )

        if created:
            # Create and save the Twine file
            fake_file = ContentFile(complex_twine_content.encode("utf-8"), name="complex_mystery.html")
            complex_twine_game.twine_file.save("complex_mystery.html", fake_file, save=False)
            complex_twine_game.save()

            complex_twine_game.categories.add(user_created_category, story_category)
            complex_twine_game.mechanics.add(story_mechanic, choice_mechanic)
            complex_twine_game.users.add(test_user)
            self.stdout.write(f" Created complex Twine game: {complex_twine_game.name}")

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("Successfully created test Twine uploads!"))
        self.stdout.write("\n TESTING CHECKLIST (Twine Files Only):")
        self.stdout.write("1. Visit individual game detail pages to see Twine games")
        self.stdout.write("2. Test that Twine games open in new tabs (current behavior)")
        self.stdout.write("3. Verify uploaded Twine games appear in game list")
        self.stdout.write("4. Test file upload process with existing UploadFileView")
        self.stdout.write("5.  Note: Embedded game upload UI not yet available (separate PR)")

        self.stdout.write("\n TEST TWINE GAMES CREATED:")
        self.stdout.write(f"   Simple: {simple_twine_game.name} (ID: {simple_twine_game.id})")
        self.stdout.write(f"   Complex: {complex_twine_game.name} (ID: {complex_twine_game.id})")
        self.stdout.write(f"   Test user: {test_user.email} / testpass123")

        self.stdout.write("\n DIRECT LINKS TO TEST:")
        self.stdout.write(f"   Simple game: http://localhost:8000/games/{simple_twine_game.id}/")
        self.stdout.write(f"   Complex game: http://localhost:8000/games/{complex_twine_game.id}/")

        self.stdout.write("\n TWINE FILES LOCATION:")
        self.stdout.write("   Check: media/twine_games/ folder for uploaded .html files")
