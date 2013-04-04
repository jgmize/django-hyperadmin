'''
These are objects generated by the resource and are serialized by a media type.
'''
from hyperadmin.links import LinkCollectorMixin, ItemLinkCollectionProvider, LinkNotAvailable


class Item(LinkCollectorMixin):
    '''
    Represents an instance that is bound to an endpoint
    '''
    form_class = None
    link_collector_class = ItemLinkCollectionProvider
    
    def __init__(self, endpoint, instance, datatap=None):
        self.endpoint = endpoint
        self.instance = instance
        self.links = self.get_link_collector()
        self.datatap = datatap
    
    @property
    def state(self):
        return self.endpoint.state
    
    def get_absolute_url(self):
        try:
            return self.endpoint.get_item_url(self)
        except LinkNotAvailable:
            return '' #or do we return None?
    
    def get_form_class(self):
        if self.form_class is not None:
            return self.form_class
        return self.endpoint.get_item_form_class()
    
    def get_form_kwargs(self, **kwargs):
        kwargs['item'] = self
        return self.endpoint.get_item_form_kwargs(**kwargs)
    
    def get_form(self, **form_kwargs):
        form_cls = self.get_form_class()
        kwargs = self.get_form_kwargs(**form_kwargs)
        form = form_cls(**kwargs)
        return form
    
    @property
    def form(self):
        """
        Mediatype uses this form to serialize the result
        """
        if not hasattr(self, '_form'):
            self._form = self.get_form()
        return self._form
    
    def get_prompt(self):
        """
        Returns a string representing the item
        """
        return self.endpoint.get_item_prompt(self)
    
    def get_resource_items(self):
        return [self]
    
    def get_namespaces(self):
        """
        Returns namespaces associated with this item
        """
        return self.endpoint.get_item_namespaces(item=self)
    
    def get_link(self, **kwargs):
        return self.endpoint.get_item_link(item=self, **kwargs)
    
    def get_outbound_link(self, **kwargs):
        kwargs.setdefault('link_factor', 'LO')
        return self.get_link(**kwargs)

