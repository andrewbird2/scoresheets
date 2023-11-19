import plotly.graph_objs as go
from affinda import AffindaAPI, TokenCredential
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, RedirectView, UpdateView

User = get_user_model()


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = "id"
    slug_url_kwarg = "id"


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    fields = ["name"]
    success_message = _("Information successfully updated")

    def get_success_url(self):
        assert self.request.user.is_authenticated  # for mypy to know that the user is authenticated
        return self.request.user.get_absolute_url()

    def get_object(self):
        return self.request.user


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail", kwargs={"pk": self.request.user.pk})


user_redirect_view = UserRedirectView.as_view()


class IdentifierForm(forms.Form):
    identifier = forms.CharField()

def get_data_from_quartet(quartet: dict):
    name = quartet.get("parsed").get("quartetName").get("parsed")
    overall = quartet.get("parsed").get("percentage").get("parsed")
    results = quartet.get("parsed").get("result")
    singing = sum([r.get("parsed").get("singingScore").get("parsed") for r in results])
    music = sum([r.get("parsed").get("musicScore").get("parsed") for r in results])
    performance = sum([r.get("parsed").get("performanceScore").get("parsed") for r in results])
    return name, overall, singing, music, performance

def scoresheet(request):
    if identifier := request.GET.get('identifier'):

        credential = TokenCredential(token=settings.AFFINDA_API_KEY)
        client = AffindaAPI(credential=credential)
        doc = client.get_document(identifier=identifier)

        all_results = [get_data_from_quartet(q) for q in doc.data.get("quartet")]
        all_results.sort(key=lambda x: x[1], reverse=True)

        competitors = [r[0] for r in all_results]
        singing_scores = [r[2] for r in all_results]
        music_scores = [r[3] for r in all_results]
        performance_scores = [r[4] for r in all_results]

        # Create traces
        fig = go.Figure()
        fig.add_trace(go.Bar(x=competitors, y=singing_scores, name='Singing'))
        fig.add_trace(go.Bar(x=competitors, y=music_scores, name='Music'))
        fig.add_trace(go.Bar(x=competitors, y=performance_scores, name='Performance'))

        # Layout adjustments
        fig.update_layout(
            title='Competition Scores by Competitor',
            xaxis_title='Competitors',
            yaxis_title='Scores',
            barmode='group'
        )
        chart = fig.to_html()
        context = {'chart': chart, 'form': IdentifierForm(),
                   "reviewUrl": doc.meta.review_url}
    else:
        context = {'form': IdentifierForm()}
    return render(request, 'pages/home.html', context=context)
