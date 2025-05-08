<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "zenodoconcepts" %>


<h2>${_('Zenodo Concept')} ${ctx.name}</h2>

<dl>
  <dt>Zenodo ID:</dt><dd>${h.external_link(f'https://zenodo.org/records/{ctx.id}', label=ctx.id)}</dd>
  <dt>DOI:</dt><dd>${h.external_link(f'https://doi.org/{ctx.doi}', label=ctx.doi)}</dd>
</dl>

% if ctx.description:
<p>
    ${ctx.description}
</p>
% endif

${request.get_datatable('contributions', h.models.Contribution, zenodoconcept=ctx).render()}
