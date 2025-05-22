from django.core.management.base import BaseCommand
from django.db import transaction

from chigame.games.models import Category, Game, Mechanic


class Command(BaseCommand):
    help = "We are creating test games specifically for testing embedded game infrastructure."

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write("Creating test embedded games...")

        word_category = Category.objects.get_or_create(name="Word Game")[0]
        puzzle_category = Category.objects.get_or_create(name="Puzzle")[0]
        arcade_category = Category.objects.get_or_create(name="Arcade")[0]
        casual_category = Category.objects.get_or_create(name="Casual")[0]

        pattern_recognition = Mechanic.objects.get_or_create(name="Pattern Recognition")[0]
        reflex_mechanic = Mechanic.objects.get_or_create(name="Reflex")[0]
        logic_mechanic = Mechanic.objects.get_or_create(name="Logic")[0]

        wordle_game, created = Game.objects.get_or_create(
            name="Wordle (Embedded)",
            defaults={
                "description": "Test Wordle game with embedded URL for testing the play infrastructure.",
                "min_players": 1,
                "max_players": 1,
                "complexity": 2.0,
                "expected_playtime": 10,
                "year_published": 2023,
                "image": "/static/images/no_picture_available.png",
                "game_url": "https://zhejiej.github.io/Words-Game/",
            },
        )
        if created:
            wordle_game.categories.add(word_category, puzzle_category)
            wordle_game.mechanics.add(pattern_recognition)
            self.stdout.write(f" Created embedded game: {wordle_game.name}")
            self.stdout.write(f"   Game URL: {wordle_game.game_url}")
            self.stdout.write(f"   Play URL: /games/{wordle_game.id}/play/")
        tetris_game, created = Game.objects.get_or_create(
            name="Tetris (Test)",
            defaults={
                "description": "Test Tetris game for testing generic embedded game infrastructure.",
                "min_players": 1,
                "max_players": 1,
                "complexity": 2.5,
                "expected_playtime": 15,
                "year_published": 2023,
                "image": "/static/images/no_picture_available.png",
                "game_url": "https://tetris.com/play-tetris",
            },
        )
        if created:
            tetris_game.categories.add(arcade_category, casual_category)
            tetris_game.mechanics.add(reflex_mechanic, pattern_recognition)
            self.stdout.write(f" Created embedded game: {tetris_game.name}")
            self.stdout.write(f"   Game URL: {tetris_game.game_url}")
            self.stdout.write(f"   Play URL: /games/{tetris_game.id}/play/")
        non_embedded_game, created = Game.objects.get_or_create(
            name="Chess (Non-Embedded)",
            defaults={
                "description": "Regular chess game without embedded URL - should show error when trying to play.",
                "min_players": 2,
                "max_players": 2,
                "complexity": 3.0,
                "expected_playtime": 45,
                "year_published": 2023,
                "image": "/static/images/no_picture_available.png",
                "game_url": "",
            },
        )
        # We also want to make sure it shows an error when the user accesses a page that does NOT have an embedded game
        if created:
            non_embedded_game.categories.add(Category.objects.get_or_create(name="Strategy")[0])
            non_embedded_game.mechanics.add(logic_mechanic)
            self.stdout.write(f"Created non-embedded game: {non_embedded_game.name}")
            self.stdout.write(f"   This should show error when accessing /games/{non_embedded_game.id}/play/")
        custom_game, created = Game.objects.get_or_create(
            name="2048 (Test)",
            defaults={
                "description": "Test 2048 game to verify generic embedded infrastructure works with different URLs.",
                "min_players": 1,
                "max_players": 1,
                "complexity": 2.0,
                "expected_playtime": 10,
                "year_published": 2023,
                "image": "/static/images/no_picture_available.png",
                "game_url": "https://play2048.co/",
            },
        )
        if created:
            custom_game.categories.add(puzzle_category, casual_category)
            custom_game.mechanics.add(logic_mechanic, pattern_recognition)
            self.stdout.write(f" Created embedded game: {custom_game.name}")
            self.stdout.write(f"   Game URL: {custom_game.game_url}")
            self.stdout.write(f"   Play URL: /games/{custom_game.id}/play/")
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("Successfully created embedded game tests!"))
        self.stdout.write("\n FIRST TESTING WORDLE URL ACCESSIBILITY...")
        try:
            import requests

            response = requests.get("https://zhejiej.github.io/Words-Game/", timeout=10)
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS(" Wordle URL is accessible and responding"))
            else:
                self.stdout.write(self.style.WARNING(f" Wordle URL returned status code: {response.status_code}"))
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f" Could not reach Wordle URL: {e}"))
        except ImportError:
            self.stdout.write(self.style.WARNING(" Install 'requests' library to test URL accessibility"))
        self.stdout.write("\n MANUAL TESTING CHECKLIST:")
        self.stdout.write("1. Visit /games/ to see the new embedded games")
        self.stdout.write("2. Check game detail pages show 'Play Game' button (PR #3)")
        self.stdout.write("3. TEST WORDLE SPECIFICALLY:")
        wordle_game = Game.objects.filter(name="Wordle (Embedded)").first()
        if wordle_game:
            self.stdout.write(f"   - Visit: http://localhost:8000/games/{wordle_game.id}/play/")
            self.stdout.write("   - Make sure that the JWT token appears in iframe URL")
            self.stdout.write("   - Then make sure the Wordle game loads and is playable")
            self.stdout.write(
                "   - Lastly just play it a bit! Try a word to make sure"
                " there are no issues with the embedding (even though its unlikey)"
            )
        self.stdout.write(
            "4.  Next is making sure that non-embedded games "
            ":(games we havent saved in the db with a link) do not show up as errors"
        )
        self.stdout.write(
            "5. Lastly - we should try different external domains "
            "to make sure that all web games are compatable for embedding."
            "I have only two that will run below but feel free to change the variables of the Chess and Tetris game!"
        )
        embedded_games = Game.objects.filter(game_url__isnull=False).exclude(game_url="")
        self.stdout.write(f"\n We have now created two games ({embedded_games.count()}):")
        for game in embedded_games:
            self.stdout.write(f"   ID {game.id}: {game.name}")
            self.stdout.write(f"      Play URL: http://localhost:8000/games/{game.id}/play/")
            if "Words-Game" in game.game_url:
                self.stdout.write(" MAIN TEST: This should load Wordle with JWT token")

        non_embedded = Game.objects.filter(name="Chess (Non-Embedded)").first()
        if non_embedded:
            self.stdout.write("\n NON-EMBEDDED TEST GAME:")
            self.stdout.write(f"   ID {non_embedded.id}: {non_embedded.name}")
            self.stdout.write(
                f"   URL: http://localhost:8000/games/{non_embedded.id}/play/ :"
                "(this should show error. We didn't save it.)"
            )

        self.stdout.write("\n QUICK TEST COMMAND:")
        if wordle_game:
            self.stdout.write(f"   Open browser to: http://localhost:8000/games/{wordle_game.id}/play/")
            self.stdout.write("   Expected: Wordle game loads in iframe with JWT token")
