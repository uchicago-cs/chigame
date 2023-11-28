from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import CreateView
from machina.apps.forum.models import Forum


class ForumCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Forum

    success_message = "Forum successfully created!"
    template_name = "forum_form.html"
    fields = ["name", "slug", "description", "image", "type"]

    def get_success_url(self):
        return "/forum"
