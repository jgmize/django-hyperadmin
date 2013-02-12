from django.utils.datastructures import SortedDict

from hyperadmin.resources import BaseResource

from hyperadmin.resources.wizard.endpoints import StepList, StepProvider


class Wizard(BaseResource):
    step_definitions = [] #tuples of Step and dictionary kwargs, kwarg must contain slug
    list_endpoint = StepList
    #CONSIDER: my resource adaptor is a wizard storage class #ie: from django.contrib.formtools.wizard.storage.
    
    @property
    def storage(self):
        if not hasattr(self, '_storage'):
            kwargs = self.get_storage_kwargs()
            self._storage = self.resource_adaptor(**kwargs)
            if not hasattr(self._storage, 'data'):
                self._storage.init_data()
        return self._storage
    
    def get_storage_kwargs(self):
        return {
            'prefix': self.get_url_name(),
            'request': self.api_request.get_django_request(),
            'file_storage': None
        }
    
    @property
    def steps(self):
        ret = list()
        for endpoint in self.endpoints.itervalues():
            if isinstance(endpoint, StepProvider):
                ret.append(endpoint)
        return ret
    
    def step_index(self, slug):
        return self.endpoints.keyOrder.index('step_%s' % slug)
    
    def get_instances(self):
        return self.steps
    
    def get_view_endpoints(self):
        endpoints = super(Wizard, self).get_view_endpoints()
        endpoints.append((self.list_endpoint, {}))
        endpoints.extend(self.step_definitions)
        return endpoints
    
    def set_step_status(self, slug, status):
        statuses = SortedDict([(slug, [status]),])
        return self.update_statuses(statuses)
    
    def update_statuses(self, statuses):
        if 'step_statuses' in self.state:
            self.state['step_statuses'].update(statuses)
        return self.set_step_statuses(statuses)
    
    @property
    def step_statuses(self):
        if 'step_statuses' not in self.state:
            self.state['step_statuses'] = self.get_step_statuses()
        return self.state['step_statuses']
    
    def get_step_statuses(self):
        data = self.storage.get_step_data('_step_statuses')
        if data is None:
            data = dict()
        for step in self.steps:
            if step.slug not in data:
                data[step.slug] = 'incomplete'
        return data
    
    def set_step_statuses(self, statuses):
        self.storage.set_step_data('_step_statuses', statuses)
    
    def get_step_data(self, key):
        return self.storage.get_step_data(key)
    
    def set_step_data(self, key, value):
        self.storage.set_step_data(key, value)
    
    def get_next_step(self, skip_steps=[], desired_step=None):
        statuses = {}
            
        for step in self.steps:
            if step.slug in skip_steps and step.can_skip():
                statuses[step.slug] = 'skipped'
            elif step.status == 'incomplete':
                if desired_step and step.slug != desired_step and step.status.can_skip():
                    #CONSIDER: this assumes we can get to our desired step
                    statuses[step.slug] = 'skipped'
                    continue
                self.update_statuses(statuses)
                return step
        self.update_statuses(statuses)
        return None
    
    def next_step(self, skip_steps=[], desired_step=None):
        step = self.get_next_step(skip_steps, desired_step)
        if step is None:
            return self.done()
        return step.get_link()
    
    def done(self):
        raise NotImplementedError

class MultiPartStep(Wizard, StepProvider):
    #main form is step control from wizard
    def __init__(self, **kwargs):
        kwargs.setdefault('adaptor', kwargs['parent'].adaptor)
        super(MultiPartStep, self).__init__(**kwargs)
    
    def get_namespaces(self):
        namespaces = super(MultiPartStep, self).get_namespaces()
        #all our substeps are namespaces
        for endpoint in self.steps:
            namespace = Namespace(name='substep-%s'% endpoint.slug, endpoint=endpoint)
            namespaces[namespace.name] = namespace
        return namespaces
    
    def get_outbound_links(self):
        links = self.create_link_collection()
        #if all steps are optional
        #link that represents continue checkout
        form_kwargs = {
            'initial': {
                'skip_steps': [self.slug],
            },
        }
        link = links.add_link(self, link_factor='LN', form_kwargs=form_kwargs, prompt='Continue')
        return links
    
    def done(self, submissions):
        self.wizard.set_step_data(self.slug, submissions)
        self.wizard.update_status(self.slug, 'complete')
        return self.wizard.next_step()
