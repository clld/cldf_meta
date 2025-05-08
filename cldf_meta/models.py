from zope.interface import implementer
from sqlalchemy import (
    Column,
    String,
    Unicode,
    Date,
    Integer,
    Boolean,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property

from clld import interfaces
from clld.db.meta import Base, CustomModelMixin, PolymorphicBaseMixin
from clld.db.models import common
from clld_glottologfamily_plugin.models import HasFamilyMixin

from cldf_meta.interfaces import ICLDFDataset, IZenodoConcept


@implementer(ICLDFDataset)
class CLDFDataset(Base, common.IdNameDescriptionMixin):
    contribution_pk = Column(Integer, ForeignKey('contribution.pk'))
    contribution = relationship('Contribution', backref='cldfdatasets')

    ord = Column(Integer)
    module = Column(Unicode)
    language_count = Column(Integer)
    glottocode_count = Column(Integer)
    parameter_count = Column(Integer)
    value_count = Column(Integer)
    form_count = Column(Integer)
    entry_count = Column(Integer)
    example_count = Column(Integer)


@implementer(interfaces.IUnit)
class DatasetLang(CustomModelMixin, common.Unit):
    pk = Column(Integer, ForeignKey('unit.pk'), primary_key=True)
    cldfdataset_pk = Column(Integer, ForeignKey('cldfdataset.pk'))
    cldfdataset = relationship('CLDFDataset', backref='datasetlangs')

    value_count = Column(Integer)
    form_count = Column(Integer)
    entry_count = Column(Integer)
    example_count = Column(Integer)


class RecordContributor(CustomModelMixin, common.ContributionContributor):
    pk = Column(Integer, ForeignKey('contributioncontributor.pk'), primary_key=True)
    role = Column(Unicode)


@implementer(interfaces.ILanguage)
class Variety(CustomModelMixin, common.Language, HasFamilyMixin):
    pk = Column(Integer, ForeignKey('language.pk'), primary_key=True)
    glottolog_id = Column(Unicode)


@implementer(IZenodoConcept)
class ZenodoConcept(Base, common.IdNameDescriptionMixin):
    doi = Column(Unicode)
    zenodo_link = Column(Unicode)


@implementer(interfaces.IContribution)
class ZenodoRecord(CustomModelMixin, common.Contribution):
    pk = Column(Integer, ForeignKey('contribution.pk'), primary_key=True)
    concept_pk = Column(Integer, ForeignKey('zenodoconcept.pk'))
    concept = relationship('ZenodoConcept', backref='contributions')

    version = Column(Unicode)
    doi = Column(Unicode)
    license = Column(Unicode)
    zenodo_link = Column(Unicode)
    zenodo_id = Column(Unicode)
    zenodo_keyword = Column(Unicode)
    zenodo_type = Column(Unicode)
    github_link = Column(Unicode)

    @property
    def primary_contributors(self):
        return [assoc.contributor for assoc in
                sorted(self.contributor_assocs,
                       key=lambda a: (a.ord, a.contributor.id))
                if assoc.primary]

    @property
    def secondary_contributors(self):
        return [assoc.contributor for assoc in
                sorted(self.contributor_assocs,
                       key=lambda a: (a.ord, a.contributor.id))
                if not assoc.primary]

    def formatted_contributors(self):
        contribs = [' and '.join(c.name for c in self.primary_contributors)]
        if self.secondary_contributors:
            contribs.append(' and '.join(c.name for c in self.secondary_contributors))
        return ' with '.join(contribs)
