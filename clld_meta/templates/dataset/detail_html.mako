<%inherit file="../home_comp.mako"/>

<h2>Welcome to the CLLD Meta Beta</h2>

<p>
  This is a catalogue of known
  ${h.external_link('https://cldf.clld.org', label='CLDF')}
  data sets which have been released on
  ${h.external_link('https://zenodo.org', label='Zenodo')}.
</p>

<p>
  You can find the underlying data and the code that created it under
  ${h.external_link('https://github.com/cldf-datasets/clld_meta')}
  on Github.
  The source code of the web app is on Github as well; you can find it under
  ${h.external_link('https://github.com/clld/clld_meta')}.
</p>
