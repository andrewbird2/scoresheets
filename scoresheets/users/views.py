from pathlib import Path

from affinda import AffindaAPI, TokenCredential
from dash import dcc, html
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, RedirectView, UpdateView
from django_plotly_dash import DjangoDash

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

import plotly.graph_objs as go



# Data for the bar chart





def scoresheet_view(request, identifier):
    app = DjangoDash('SimpleExample')  # replaces dash.Dash
    credential = TokenCredential(token=settings.AFFINDA_API_KEY)
    client = AffindaAPI(credential=credential)
    doc = client.get_document(identifier=identifier)
    data = [(quartet.get("parsed").get("quartetName").get("parsed"), quartet.get("parsed").get("percentage").get("parsed")) for quartet in doc.data.get("quartet")]

    app.layout = html.Div([
        dcc.Graph(
            id='bar-chart',
            figure={
                'data': [
                    go.Bar(
                        x=[item[0] for item in data],  # labels
                        y=[item[1] for item in data],  # values
                        # marker={'color': ['blue', 'green']}  # bar colors
                    )
                ],
                'layout': go.Layout(
                    title='A silly little chart',
                    xaxis={'title': 'Groups'},
                    yaxis={'title': 'Values'},
                    margin={'l': 40, 'b': 40, 't': 40, 'r': 10},
                    hovermode='closest'
                )
            }
        )
    ])
    return render(request, 'pages/home.html', {'doc': doc})
