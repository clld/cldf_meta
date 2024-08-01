<%inherit file="home_comp.mako"/>
<%namespace name="util" file="util.mako"/>

<h3>Downloads</h3>

## TODO set zenodo doi and version once we have one
## Copy-pasted note from the implementation of util.dataset_download for future
## reference:
##
## Download info for datasets archived with Zenodo.
## It uses the following data specified in the clld section of appconf.ini:
## - zenodo_concept_doi
## - zenodo_version_doi (optional)
## - zenodo_version_tag (optional)
## - dataset_github_repos
% if req.registry.settings.get('clld.zenodo_concept_doi'):
${util.dataset_download()}
% else:
<p>
  You can find the latest development version of the <em>CLLD Meta</em> data
  ${h.external_link('https://github.com/cldf-datasets/clld_meta', label='on GitHub')}
</p>
% endif
