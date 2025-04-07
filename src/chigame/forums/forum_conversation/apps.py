from machina.apps.forum_conversation.apps import ForumConversationAppConfig as BaseForumConversationAppConfig


class ForumConversationConfig(BaseForumConversationAppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "chigame.forum_conversation"
