# vim: tabstop=4 shiftwidth=4 softtabstop=4

#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import tabs

from openstack_dashboard import api
from .forms import CreateRack, EditRack
from .tabs import RackDetailTabs


LOG = logging.getLogger(__name__)


class CreateView(forms.ModalFormView):
    form_class = CreateRack
    template_name = 'infrastructure/resource_management/racks/create.html'
    success_url = reverse_lazy(
        'horizon:infrastructure:resource_management:index')


class EditView(forms.ModalFormView):
    form_class = EditRack
    template_name = 'infrastructure/resource_management/racks/edit.html'
    success_url = reverse_lazy(
        'horizon:infrastructure:resource_management:index')

    def get_context_data(self, **kwargs):
        context = super(EditView, self).get_context_data(**kwargs)
        context['rack_id'] = self.kwargs['rack_id']
        return context

    def get_initial(self):
        try:
            rack = api.management.Rack.get(self.request,
                                           self.kwargs['rack_id'])
        except:
            exceptions.handle(self.request,
                              _("Unable to retrieve rack data."))
        return {'rack_id': rack.id,
                'name': rack.name,
                'resource_class_id': rack.resource_class_id,
                'location': rack.location,
                'subnet': rack.subnet}


class DetailView(tabs.TabView):
    tab_group_class = RackDetailTabs
    template_name = 'infrastructure/resource_management/racks/detail.html'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context["rack"] = self.get_data()
        return context

    def get_data(self):
        if not hasattr(self, "_rack"):
            try:
                rack_id = self.kwargs['rack_id']
                rack = api.management.Rack.get(self.request, rack_id)
            except:
                redirect = reverse('horizon:infrastructure:'
                                   'resource_management:index')
                exceptions.handle(self.request,
                                  _('Unable to retrieve details for '
                                    'rack "%s".')
                                    % rack_id,
                                    redirect=redirect)
            self._rack = rack
        return self._rack

    def get_tabs(self, request, *args, **kwargs):
        rack = self.get_data()
        return self.tab_group_class(request, rack=rack,
                                    **kwargs)