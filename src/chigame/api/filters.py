import django_filters
from django_filters import BaseInFilter

from chigame.games.models import Game


class GameFilter(django_filters.FilterSet):
    # https://www.w3schools.com/django/ref_lookups_icontains.php
    # icontains: case-insensitive containment test
    name = django_filters.CharFilter(lookup_expr="icontains")

    year_published = django_filters.NumberFilter(lookup_expr="exact")
    year_published__gte = django_filters.NumberFilter(field_name="year_published", lookup_expr="gte")
    year_published__lte = django_filters.NumberFilter(field_name="year_published", lookup_expr="lte")

    suggested_age = django_filters.NumberFilter(lookup_expr="exact")
    suggested_age__gte = django_filters.NumberFilter(field_name="suggested_age", lookup_expr="gte")
    suggested_age__lte = django_filters.NumberFilter(field_name="suggested_age", lookup_expr="lte")

    expected_playtime = django_filters.NumberFilter(lookup_expr="exact")
    expected_playtime__gte = django_filters.NumberFilter(field_name="expected_playtime", lookup_expr="gte")
    expected_playtime__lte = django_filters.NumberFilter(field_name="expected_playtime", lookup_expr="lte")

    min_playtime = django_filters.NumberFilter(lookup_expr="exact")
    min_playtime__gte = django_filters.NumberFilter(field_name="min_playtime", lookup_expr="gte")
    min_playtime__lte = django_filters.NumberFilter(field_name="min_playtime", lookup_expr="lte")

    max_playtime = django_filters.NumberFilter(lookup_expr="exact")
    max_playtime__gte = django_filters.NumberFilter(field_name="max_playtime", lookup_expr="gte")
    max_playtime__lte = django_filters.NumberFilter(field_name="max_playtime", lookup_expr="lte")

    min_players = django_filters.NumberFilter(lookup_expr="exact")
    min_players__gte = django_filters.NumberFilter(field_name="min_players", lookup_expr="gte")
    min_players__lte = django_filters.NumberFilter(field_name="min_players", lookup_expr="lte")

    max_players__gte = django_filters.NumberFilter(field_name="max_players", lookup_expr="gte")
    max_players__lte = django_filters.NumberFilter(field_name="max_players", lookup_expr="lte")

    complexity = django_filters.NumberFilter(lookup_expr="exact")
    complexity__gte = django_filters.NumberFilter(field_name="complexity", lookup_expr="gte")
    complexity__lte = django_filters.NumberFilter(field_name="complexity", lookup_expr="lte")

    BGG_id = django_filters.NumberFilter(lookup_expr="exact")

    max_players__in = BaseInFilter(field_name="max_players", lookup_expr="in")
    min_players__in = BaseInFilter(field_name="min_players", lookup_expr="in")
    complexity__in = BaseInFilter(field_name="complexity", lookup_expr="in")
    year_published__in = BaseInFilter(field_name="year_published", lookup_expr="in")
    suggested_age__in = BaseInFilter(field_name="suggested_age", lookup_expr="in")
    expected_playtime__in = BaseInFilter(field_name="expected_playtime", lookup_expr="in")
    min_playtime__in = BaseInFilter(field_name="min_playtime", lookup_expr="in")
    max_playtime__in = BaseInFilter(field_name="max_playtime", lookup_expr="in")
    BGG_id__in = BaseInFilter(field_name="BGG_id", lookup_expr="in")

    class Meta:
        model = Game
        fields = [
            "name",
            "year_published",
            "year_published__in",
            "suggested_age",
            "suggested_age__in",
            "expected_playtime",
            "expected_playtime__in",
            "min_playtime",
            "min_playtime__in",
            "max_playtime",
            "max_playtime__in",
            "complexity",
            "complexity__in",
            "min_players",
            "min_players__in",
            "max_players",
            "max_players__in",
            "BGG_id",
            "BGG_id__in",
        ]
