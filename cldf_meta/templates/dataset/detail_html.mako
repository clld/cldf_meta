<%inherit file="../home_comp.mako"/>
<%block name="title">Welcome</%block>

<h2>Welcome to the CLDF Meta Database<sup><i>beta</i></sup></h2>

<p>
  This is a catalogue of known
  ${h.external_link('https://cldf.clld.org', label='CLDF')}
  data sets which have been released on
  ${h.external_link('https://zenodo.org', label='Zenodo')}.
</p>

<p>
  You can find the underlying data and the code that created it under
  ${h.external_link('https://github.com/cldf-datasets/cldf_meta')}
  on Github.
  The source code of the web app is on Github as well; you can find it under
  ${h.external_link('https://github.com/clld/cldf_meta')}.
</p>

<p>
  If you want to know more about the ins and outs of the project, have a look at
  <a href="${request.route_url('overview')}">the overview</a>.
</p>

<h3>How to cite this project</h3>

## TODO(johannes): add actual Zenodo citation once it exists
<p>
  Eventually this project will be released on Zenodo and get properly versioned
  DOIs.
  Until then the following BibTeX snippet can serve as a possible interim
  citation:
</p>

<pre>
@misc{cldf_meta,
  author = {Johannes Englisch},
  year = {forthcoming},
  title = {{CLDF-Meta}: A catalogue of {CLDF} databases},
  note = {Available online at https://meta.clld.org and https://github.com/cldf-datasets/cldf\_meta},
  url = {https://meta.clld.org},
}
</pre>
