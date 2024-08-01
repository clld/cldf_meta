from sqlalchemy.sql.expression import case

from clld.db.models import common
from clld.web import datatables
from clld.web.datatables.base import LinkCol, Col, LinkToMapCol, DataTable
from clld.web.datatables.contribution import ContributorsCol
from clld.web.util.helpers import external_link, link
from clld_glottologfamily_plugin.datatables import FamilyCol

from clld_meta import models


# Columns

class CountCol(Col):
    __kw__ = {
        'input_size': 'mini',
        'sClass': 'right'}

    def get_value(self, item):
        return super().get_value(item) or 0

    def order(self):
        # When a count is missing, assume there are 0 counted things.
        return case(
            [(self.model_col.is_(None), 0)],
            else_=self.model_col)


class OrdCol(Col):
    __kw__ = {
        'input_size': 'mini',
        'sClass': 'right'}

    def format(self, item):
        obj = self.get_obj(item)
        return link(self.dt.req, obj, label=item.ord) if obj else ''


class GlottocodeCol(Col):

    def format(self, item):
        item = self.get_obj(item)
        if item.glottolog_id:
            return external_link(
                'http://glottolog.org/resource/languoid/id/{}'.format(
                    item.glottolog_id),
                label=item.glottolog_id,
                title='Language information at Glottolog')
        else:
            return ''


class DOICol(Col):

    def format(self, item):
        item = self.get_obj(item)
        if item.doi:
            return external_link(
                f'https://doi.org/{item.doi}', label=item.doi, title='DOI')
        else:
            return ''


class ZenodoLinkCol(Col):

    def format(self, item):
        item = self.get_obj(item)
        if item.zenodo_link:
            return external_link(
                item.zenodo_link,
                label=item.zenodo_link,
                title='Zenodo')
        else:
            return ''


class UnitCol(Col):

    """Column which renders a link."""

    def get_attrs(self, item):
        return {}

    def format(self, item):
        obj = self.get_obj(item)
        return link(self.dt.req, obj, **self.get_attrs(item)) if obj else ''


# Tables

class CLDFDatasets(DataTable):
    # TODO: filter by language?

    __constraints__ = [common.Contribution]

    def base_query(self, query):
        if self.contribution:
            query = query.filter(
                models.CLDFDataset.contribution_pk == self.contribution.pk)
        else:
            query = query.join(common.Contribution)
        return query

    def col_defs(self):
        # FIXME: not happy with that...
        #  * ord needs a better name ('number'? 'revision'?)
        #    ^ maybe i should just show the *version number*
        #    ^ nah, that doesn't work -- ord is about multiple datasets in *the
        #      same record*
        ord = OrdCol(self, 'ord')
        module = Col(self, 'module')
        language_count = CountCol(
            self, 'language_count', sTitle='#&#160;Languages',
            model_col=models.CLDFDataset.language_count)
        glottocode_count = CountCol(
            self, 'glottocode_count', sTitle='#&#160;Glottocodes',
            model_col=models.CLDFDataset.glottocode_count)
        parameter_count = CountCol(
            self, 'parameter_count', sTitle='#&#160;Parameters',
            model_col=models.CLDFDataset.parameter_count)
        value_count = CountCol(
            self, 'value_count', sTitle='#&#160;Values',
            model_col=models.CLDFDataset.value_count)
        form_count = CountCol(
            self, 'form_count', sTitle='#&#160;Forms',
            model_col=models.CLDFDataset.form_count)
        entry_count = CountCol(
            self, 'entry_count', sTitle='#&#160;Entries',
            model_col=models.CLDFDataset.entry_count)
        example_count = CountCol(
            self, 'example_count', sTitle='#&#160;Examples',
            model_col=models.CLDFDataset.example_count)
        if self.contribution:
            return [
                ord, module, language_count, glottocode_count, parameter_count,
                value_count, form_count, entry_count, example_count]
        else:
            contribution = LinkCol(
                self, 'contribution',
                model_col=common.Contribution.name,
                get_object=lambda o: o.contribution)
            return [
                contribution, ord, module, language_count, glottocode_count,
                parameter_count, value_count, form_count, entry_count,
                example_count]


class Contributions(datatables.Contributions):

    __constraints__ = [models.ZenodoConcept]

    def base_query(self, query):
        if self.zenodoconcept:
            query = query.filter(
                models.ZenodoRecord.concept_pk == self.zenodoconcept.pk)
        else:
            query = query.join(models.ZenodoRecord.concept)
        return query

    def col_defs(self):
        name = LinkCol(self, 'name')
        people = ContributorsCol(self, 'contributor')
        version = Col(self, 'version')
        doi = DOICol(self, 'doi', sTitle='DOI')
        # TODO: show record number instead of name?
        concept = LinkCol(
            self, 'concept',
            sTitle='Zenodo Concept',
            model_col=models.ZenodoConcept.name,
            get_object=lambda o: o.concept)
        return [name, people, version, doi, concept]


class DatasetLangs(datatables.Units):

    __constraints__ = [common.Language, models.CLDFDataset]

    def base_query(self, query):
        if self.language:
            query = query.filter(
                models.DatasetLang.language_pk == self.language.pk)
        else:
            query = query.join(common.Language)
        if self.cldfdataset:
            query = query.filter(
                models.DatasetLang.cldfdataset_pk == self.cldfdataset.pk)
        else:
            query = query.join(models.CLDFDataset)
        return query

    def col_defs(self):
        # FIXME: showing these non-descript dataset ids is not ideal
        dataset = LinkCol(
            self, 'dataset',
            model_col=models.CLDFDataset.id,
            get_object=lambda o: o.cldfdataset)
        language = LinkCol(
            self, 'language',
            model_col=common.Language.name,
            get_object=lambda o: o.language)
        value_count = CountCol(
            self, 'value_count', sTitle='#&#160;1Values',
            model_col=models.DatasetLang.value_count)
        form_count = CountCol(
            self, 'form_count', sTitle='#&#160;1Forms',
            model_col=models.DatasetLang.form_count)
        entry_count = CountCol(
            self, 'entry_count', sTitle='#&#160;1Entries',
            model_col=models.DatasetLang.entry_count)
        example_count = CountCol(
            self, 'example_count', sTitle='#&#160;1Examples',
            model_col=models.DatasetLang.example_count)
        if self.language:
            module = Col(
                self, 'module', model_col=models.CLDFDataset.module,
                get_object=lambda o: o.cldfdataset)
            return [
                dataset, module, value_count, form_count, entry_count,
                example_count]
        elif self.cldfdataset:
            return [
                language, value_count, form_count, entry_count, example_count]
        else:
            return [
                dataset, language, value_count, form_count, entry_count,
                example_count]


class Languages(datatables.Languages):

    def base_query(self, query):
        return query.outerjoin(models.Variety.family)

    def col_defs(self):
        # NOTE: can't be named 'glottocode' because Language.glottocode is a
        # Python property instead of a sqlalchemy table column.
        name = LinkCol(self, 'name')
        glottocode = GlottocodeCol(
            self,
            'glottocode_col',
            model_col=models.Variety.glottolog_id,
            sTitle='Glottocode')
        family = FamilyCol(self, 'family', models.Variety)
        linktomap = LinkToMapCol(self, 'm')
        return [name, glottocode, family, linktomap]


class ZenodoConcepts(DataTable):

    def base_query(self, query):
        return query

    def col_defs(self):
        zenodo_id = ZenodoLinkCol(self, 'zenodo_id', sTitle='Zenodo ID')
        name = LinkCol(self, 'name')
        doi = DOICol(self, 'id', sTitle='DOI')
        # TODO: count individual records
        return [zenodo_id, name, doi]


def includeme(config):
    """register custom datatables"""
    config.register_datatable('cldfdatasets', CLDFDatasets)
    config.register_datatable('contributions', Contributions)
    config.register_datatable('languages', Languages)
    config.register_datatable('units', DatasetLangs)
    config.register_datatable('zenodoconcepts', ZenodoConcepts)
