from hyperadmin.resources.endpoints import LinkPrototype, Endpoint


class ListLinkPrototype(LinkPrototype):
    def get_link_kwargs(self, **kwargs):
        link_kwargs = {'url':self.get_url(),
                       'resource':self,
                       'prompt':'list',
                       'rel':'list',}
        link_kwargs.update(kwargs)
        return super(ListLinkPrototype, self).get_link_kwargs(**link_kwargs)

class CreateLinkPrototype(LinkPrototype):
    def show_link(self, **kwargs):
        return self.resource.has_add_permission()
    
    def get_link_kwargs(self, **kwargs):
        kwargs = super(CreateLinkPrototype, self).get_link_kwargs(**kwargs)
        
        link_kwargs = {'url':self.get_url(),
                       'resource':self,
                       'on_submit':self.handle_submission,
                       'method':'POST',
                       'form_class': self.resource.get_form_class(),
                       'prompt':'create',
                       'rel':'create',}
        link_kwargs.update(kwargs)
        return super(CreateLinkPrototype, self).get_link_kwargs(**link_kwargs)

#TODO consider: Update vs Detail link
class UpdateLinkPrototype(LinkPrototype):
    def show_link(self, **kwargs):
        return self.resource.has_change_permission(item=kwargs.get('item', None))
    
    def get_link_kwargs(self, **kwargs):
        item = kwargs.get('item')
        
        kwargs = super(UpdateLinkPrototype, self).get_link_kwargs(**kwargs)
        
        link_kwargs = {'url':self.get_url(item=item),
                       'resource':self,
                       'on_submit':self.handle_submission,
                       'method':'POST',
                       'form_class': item.get_form_class(),
                       'prompt':'update',
                       'rel':'update',}
        link_kwargs.update(kwargs)
        return super(UpdateLinkPrototype, self).get_link_kwargs(**link_kwargs)

class DeleteLinkPrototype(LinkPrototype):
    def show_link(self, **kwargs):
        return self.resource.has_delete_permission(item=kwargs.get('item', None))
    
    def get_link_kwargs(self, **kwargs):
        item = kwargs.get('item')
        
        kwargs = super(DeleteLinkPrototype, self).get_link_kwargs(**kwargs)
        
        link_kwargs = {'url':self.get_url(item=item),
                       'resource':self,
                       'on_submit':self.handle_submission,
                       'method':'POST',
                       'prompt':'delete',
                       'rel':'delete',}
        link_kwargs.update(kwargs)
        return super(DeleteLinkPrototype, self).get_link_kwargs(**link_kwargs)
    
    def handle_submission(self, link, submit_kwargs):
        instance = self.resource.state.item.instance
        instance.delete()
        return self.on_success()

class ListEndpoint(Endpoint):
    name_suffix = 'list'
    url_suffix = r'^$'
    
    def get_view_class(self):
        return self.resource.list_view
    
    def get_links(self):
        return {'list':ListLinkPrototype(endpoint=self),
                'rest-create':CreateLinkPrototype(endpoint=self),}
    
    def get_outbound_links(self):
        links = self.create_link_collection()
        links.add_link('create', link_factor='LO')
        return links

class CreateEndpoint(Endpoint):
    name_suffix = 'add'
    url_suffix = r'^add/$'
    
    def get_view_class(self):
        return self.resource.add_view
    
    def get_links(self):
        return {'create':CreateLinkPrototype(endpoint=self)}

class DetailEndpoint(Endpoint):
    name_suffix = 'detail'
    url_suffix = r'^(?P<pk>\w+)/$'
    
    def get_view_class(self):
        return self.resource.detail_view
    
    def get_links(self):
        return {'update':UpdateLinkPrototype(endpoint=self),
                'rest-update':UpdateLinkPrototype(endpoint=self, link_kwargs={'method':'PUT'}),
                'rest-delete':DeleteLinkPrototype(endpoint=self, link_kwargs={'method':'DELETE'}),}
    
    def get_item_outbound_links(self, item):
        links = self.create_link_collection()
        links.add_link('delete', item=item, link_factor='LO')
        return links
    
    def get_url(self, item):
        return super(DetailEndpoint, self).get_url(pk=item.instance.pk)

class DeleteEndpoint(Endpoint):
    name_suffix = 'delete'
    url_suffix = r'^(?P<pk>\w+)/delete/$'
    
    def get_view_class(self):
        return self.resource.delete_view
    
    def get_links(self):
        return {'delete':DeleteLinkPrototype(endpoint=self)}
    
    def get_url(self, item):
        return super(DeleteEndpoint, self).get_url(pk=item.instance.pk)
