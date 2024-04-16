import collections
from functools import partial

from pyramid.config import Configurator

from clld.interfaces import IDomainElement, IMapMarker, IValueSet, IValue
from clld.web.app import menu_item
from clld_glottologfamily_plugin import util
from clldutils.svg import pie, icon, data_url

# we must make sure custom models are known at database initialization!
from clld_meta import models
from clld_meta.interfaces import ICLDFDataset, IZenodoConcept


_ = lambda s: s
_('Contribution')
_('Contributions')
_('CLDF Dataset')
_('CLDF Datasets')
_('Zenodo Concept')
_('Zenodo Concepts')
_('Unit')
_('Units')


class LanguageByFamilyMapMarker(util.LanguageByFamilyMapMarker):

    def __call__(self, ctx, req):
        if IValueSet.providedBy(ctx):
            c = collections.Counter(
                v.domainelement.jsondata['color'] for v in ctx.values)
            return data_url(pie(
                *list(zip(*[(v, k) for k, v in c.most_common()])),
                stroke_circle=True))
        if IDomainElement.providedBy(ctx):
            return data_url(icon(
                ctx.jsondata['color'].replace('#', 'c')))
        if IValue.providedBy(ctx):
            return data_url(icon(
                ctx.domainelement.jsondata['color'].replace('#', 'c')))
        return super().__call__(ctx, req)

    def get_icon(self, ctx, req):
        if IValueSet.providedBy(ctx):
            icons = [
                v.domainelement.jsondata['icon']
                for v in ctx.values
                if v.domainelement]
            # FIXME this only shows the *first* value
            return icons[0] if len(icons) > 0 else None
        elif IDomainElement.providedBy(ctx):
            return ctx.jsondata['icon']
        elif IValue.providedBy(ctx) and ctx.domainelement:
            return ctx.domainelement.jsondata['icon']
        else:
            return super().get_icon(ctx, req)


def main(global_config, **settings):
    """This function returns a Pyramid WSGI application."""
    config = Configurator(settings=settings)
    config.include('clld.web.app')
    config.include('clld_glottologfamily_plugin')
    config.include('clldmpg')

    config.register_menu(
        ('dataset', partial(menu_item, 'dataset', label='Home')),
        ('zenodoconcepts', partial(menu_item, 'zenodoconcepts', label=_('Zenodo Concepts'))),
        ('contributions', partial(menu_item, 'contributions')),
        ('cldfdatasets', partial(menu_item, 'cldfdatasets', label=_('CLDF Datasets'))),
        ('languages', partial(menu_item, 'languages')),
    )

    config.registry.registerUtility(LanguageByFamilyMapMarker(), IMapMarker)

    config.register_resource(
        'cldfdataset', models.CLDFDataset, ICLDFDataset, with_index=True)
    config.register_resource(
        'zenodoconcept', models.ZenodoConcept, IZenodoConcept, with_index=True)

    return config.make_wsgi_app()
