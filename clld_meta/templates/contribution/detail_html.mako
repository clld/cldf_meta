<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "contributions" %>
<%! import clld_meta.models as m %>

<h2>${_('Contribution')} ${ctx.name}</h2>
<dl>
  <dt>Link to Zenodo</dt>
  <dd>${h.external_link(ctx.zenodo_link, label=ctx.zenodo_link)}</dd>
  <dt>DOI</dt>
  <dd>${h.external_link(f'https://doi.org/{ctx.doi}', label=ctx.doi)}</dd>
  <dt>Zenodo concept</dt>
  <dd>${h.link(request, ctx.concept)}</dd>
  % if ctx.github_link:
  <dt>GitHub link:</dt>
  <dd>${h.external_link(ctx.github_link)}"</dd>
  % endif
</dl>

<%def name="sidebar()">
  <div class="well well-small">
    <% all_versions = h.DBSession.query(m.ZenodoRecord).filter(m.ZenodoRecord.concept_pk == ctx.concept_pk) %>
    <p>Dataset versions</p>
    <ul>
    % for v in all_versions:
      % if v == ctx:
      <li><strong>${v.version}</strong></li>
      % else:
      <li>${h.link(request, v, label=v.version)}</li>
      % endif
    % endfor
    </ul>
  </div>
</%def>

<% dataset_table = request.get_datatable('cldfdatasets', m.CLDFDataset, contribution=ctx) %>
% if dataset_table:
<h3>${_('CLDF Datasets')}</h3>
<div>
  ${dataset_table.render()}
</div>
% endif
