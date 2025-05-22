from django.core.management.base import BaseCommand
from django.db import transaction

from chigame.games.models import Category, Game, Mechanic, Person


class Command(BaseCommand):
    help = "Creates sample games for testing the recommendation system"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write("Creating test categories...")
        categories = {
            "strategy": Category.objects.get_or_create(name="Strategy")[0],
            "family": Category.objects.get_or_create(name="Family")[0],
            "party": Category.objects.get_or_create(name="Party")[0],
            "card_game": Category.objects.get_or_create(name="Card Game")[0],
            "adventure": Category.objects.get_or_create(name="Adventure")[0],
            "fantasy": Category.objects.get_or_create(name="Fantasy")[0],
            "sci_fi": Category.objects.get_or_create(name="Science Fiction")[0],
        }

        self.stdout.write("Creating test mechanics...")
        mechanics = {
            "deck_building": Mechanic.objects.get_or_create(name="Deck Building")[0],
            "worker_placement": Mechanic.objects.get_or_create(name="Worker Placement")[0],
            "dice_rolling": Mechanic.objects.get_or_create(name="Dice Rolling")[0],
            "hand_mgmt": Mechanic.objects.get_or_create(name="Hand Management")[0],
            "area_control": Mechanic.objects.get_or_create(name="Area Control")[0],
        }

        self.stdout.write("Creating test designers...")
        designers = {
            "reiner": Person.objects.get_or_create(name="Reiner Knizia", person_role=1)[0],
            "uwe": Person.objects.get_or_create(name="Uwe Rosenberg", person_role=1)[0],
            "matt": Person.objects.get_or_create(name="Matt Leacock", person_role=1)[0],
        }

        game1, created = Game.objects.get_or_create(
            name="CardTactics",
            defaults={
                "description": "A strategic card game where players build armies and battle for control.",
                "min_players": 2,
                "max_players": 4,
                "complexity": 3.5,
                "expected_playtime": 60,
                "year_published": 2020,
                "image": "/static/images/no_picture_available.png",
            },
        )

        if created:
            game1.categories.add(categories["strategy"], categories["card_game"])
            game1.mechanics.add(mechanics["deck_building"], mechanics["hand_mgmt"])
            game1.people.add(designers["reiner"])
            self.stdout.write(f"Created game: {game1.name}")

        game2, created = Game.objects.get_or_create(
            name="Battle Masters",
            defaults={
                "description": "Build your deck and outmaneuver your opponent in this tactical card game.",
                "min_players": 2,
                "max_players": 4,
                "complexity": 3.2,
                "expected_playtime": 70,
                "year_published": 2021,
                "image": "/static/images/no_picture_available.png",
            },
        )

        if created:
            game2.categories.add(categories["strategy"], categories["card_game"])
            game2.mechanics.add(mechanics["deck_building"], mechanics["hand_mgmt"])
            game2.people.add(designers["reiner"])
            self.stdout.write(f"Created game: {game2.name}")

        game3, created = Game.objects.get_or_create(
            name="Farmland Empire",
            defaults={
                "description": "Build your farm and place workers to optimize your production.",
                "min_players": 2,
                "max_players": 5,
                "complexity": 3.8,
                "expected_playtime": 90,
                "year_published": 2019,
                "image": "/static/images/no_picture_available.png",
            },
        )

        if created:
            game3.categories.add(categories["strategy"])
            game3.mechanics.add(mechanics["worker_placement"])
            game3.people.add(designers["uwe"])
            self.stdout.write(f"Created game: {game3.name}")

        game4, created = Game.objects.get_or_create(
            name="Cosmic Explorers",
            defaults={
                "description": "Explore new planets and build your space empire in this sci-fi adventure.",
                "min_players": 2,
                "max_players": 6,
                "complexity": 4.0,
                "expected_playtime": 120,
                "year_published": 2022,
                "image": "/static/images/no_picture_available.png",
            },
        )

        if created:
            game4.categories.add(categories["adventure"], categories["sci_fi"])
            game4.mechanics.add(mechanics["area_control"], mechanics["dice_rolling"])
            game4.people.add(designers["matt"])
            self.stdout.write(f"Created game: {game4.name}")

        game5, created = Game.objects.get_or_create(
            name="Family Fun Night",
            defaults={
                "description": "A light-hearted family game with simple rules and lots of laughs.",
                "min_players": 3,
                "max_players": 8,
                "complexity": 1.5,
                "expected_playtime": 30,
                "year_published": 2023,
                "image": "/static/images/no_picture_available.png",
            },
        )

        if created:
            game5.categories.add(categories["family"], categories["party"])
            game5.mechanics.add(mechanics["dice_rolling"])
            game5.people.add(designers["matt"])
            self.stdout.write(f"Created game: {game5.name}")

        self.stdout.write("Creating Wordle word game...")
        word_category = Category.objects.get_or_create(name="Word Game")[0]
        puzzle_category = Category.objects.get_or_create(name="Puzzle")[0]
        single_player_mechanic = Mechanic.objects.get_or_create(name="Pattern Recognition")[0]
        wordle_game, created = Game.objects.get_or_create(
            name="Wordle",
            defaults={
                "description": "A word guessing game where you try to guess a 5-letter word in 6 attempts.",
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
            wordle_game.mechanics.add(single_player_mechanic)
            self.stdout.write(f"Created game: {wordle_game.name}")

        self.stdout.write(self.style.SUCCESS("Successfully created test games"))
