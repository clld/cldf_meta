<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "cldfdatasets" %>

<h2>${_('CLDF Dataset')} ${ctx.id}</h2>

<div>
  <dt>${_('Contribution')}</dt>
  <dd>${h.link(request, ctx.contribution)} (${ctx.contribution.version})</dd>
  <dt>Number</dt>
  <dd>${ctx.ord}</dd>
</div>

<h3>Languages</h3>

<% language_table = request.get_datatable('units', h.models.Unit, cldfdataset=ctx) %>
% if language_table:
<div>
  ${language_table.render()}
</div>
% endif
