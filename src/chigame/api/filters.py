import django_filters

from chigame.games.models import Game


class GameFilter(django_filters.FilterSet):
    # https://www.w3schools.com/django/ref_lookups_icontains.php
    # icontains: case-insensitive containment test
    name = django_filters.CharFilter(lookup_expr="icontains")

    year_published = django_filters.NumberFilter(lookup_expr="exact")
    suggested_age = django_filters.NumberFilter(lookup_expr="exact")
    expected_playtime = django_filters.NumberFilter(lookup_expr="exact")
    min_playtime = django_filters.NumberFilter(lookup_expr="exact")
    max_playtime = django_filters.NumberFilter(lookup_expr="exact")
    min_players = django_filters.NumberFilter(lookup_expr="exact")
    max_players = django_filters.NumberFilter(lookup_expr="exact")

    complexity = django_filters.NumberFilter(lookup_expr="exact")
    complexity__gte = django_filters.NumberFilter(field_name="complexity", lookup_expr="gte")
    complexity__lte = django_filters.NumberFilter(field_name="complexity", lookup_expr="lte")

    BGG_id = django_filters.NumberFilter(lookup_expr="exact")

    class Meta:
        model = Game
        fields = [
            "name",
            "year_published",
            "suggested_age",
            "expected_playtime",
            "min_playtime",
            "max_playtime",
            "complexity",
            "min_players",
            "max_players",
            "BGG_id",
        ]
