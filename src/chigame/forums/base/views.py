from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.views.generic import CreateView

from .forms import ForumForm


class ForumCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    form_class = ForumForm
    success_message = "Forum successfully created!"
    template_name = "forum_form.html"

    def get_success_url(self):
        return reverse("forum:index")
