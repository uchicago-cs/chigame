from background_task import background

from .models import Lobby


@background(schedule=1)
def decrement_time_constraint(lobby_pk):
    try:
        lobby = Lobby.objects.get(pk=lobby_pk)
        if lobby.time_constraint > 0:
            lobby.time_constraint -= 1
            lobby.save()
    except Exception as e:
        print(f"Error in task: {e}")
