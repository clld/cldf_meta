import collections
import unicodedata
import sys
from itertools import chain

import sqlalchemy

from clld.cliutil import Data
from clld.db.meta import DBSession
from clld.db.models import common
from clld_glottologfamily_plugin.util import load_families

import cldfcatalog
from pyglottolog import Glottolog

from cldf_meta import models

CLDF_ID = 'http://cldf.clld.org/v1.0/terms.rdf#id'
CLDF_NAME = 'http://cldf.clld.org/v1.0/terms.rdf#name'
CLDF_DESC = 'http://cldf.clld.org/v1.0/terms.rdf#description'
CLDF_GLOTTOCODE = 'http://cldf.clld.org/v1.0/terms.rdf#glottocode'
CLDF_CONTRIB_ID = 'http://cldf.clld.org/v1.0/terms.rdf#contributionReference'
CLDF_LANG_ID = 'http://cldf.clld.org/v1.0/terms.rdf#languageReference'


def slug(s):
    return ''.join(
        c
        for c in unicodedata.normalize('NFKD', s).lower()
        if c in 'abcdefghijklmnopqrstuvwxyz0123456789 -_')


def make_zenodo_concepts(cldf_contributions):
    zenodo_concepts = {}
    # use info from the most recent record of a concept
    for contrib in sorted(
        cldf_contributions, key=lambda c: -int(c['Zenodo_ID']),
    ):
        concept_id = contrib['Concept_ID']
        if concept_id not in zenodo_concepts:
            zenodo_concepts[concept_id] = models.ZenodoConcept(
                id=concept_id,
                name=contrib['Name'],
                doi=contrib['Concept_DOI'],
                zenodo_link=f'https://zenodo.org/records/{concept_id}')
    return zenodo_concepts


def make_contributors(cldf_contributions):
    # NOTE(johannes): The usual caveats to naive name handling apply:
    #  * people with the same name are considered the same person
    #  * a person with changing names, spelling variants, etc. is considered
    #    multiple people
    people = collections.defaultdict(set)
    people[slug('Johannes Englisch')].add('Johannes Englisch')
    for contribution in cldf_contributions:
        for name in contribution.get('Creators', ()):
            people[slug(name).replace(' ', '-')].add(name)
        for name in contribution.get('Contributors', ()):
            people[slug(name).replace(' ', '-')].add(name)
    return {
        name: common.Contributor(
            id=f'{person_id}-{number}' if len(names) > 1 else person_id,
            name=name)
        for person_id, names in people.items()
        for number, name in enumerate(sorted(names))}


def get_languoid(languoids, glottocode):
    if (languoid := languoids.get(glottocode)):
        return languoid
    else:
        print(
            'glottocode not in glottolog:', glottocode,
            '(is glottolog up-to-date?)',
            file=sys.stderr)
        return None


def make_languages(cldf_languages, languoids):
    return {
        cldf_language['ID']: models.Variety(
            id=cldf_language['ID'],
            glottolog_id=glottocode,
            name=languoid.name,
            latitude=languoid.latitude,
            longitude=languoid.longitude)
        for cldf_language in cldf_languages.values()
        if (glottocode := cldf_language.get('Glottocode'))
        and (languoid := get_languoid(languoids, glottocode))}


def make_contributions(cldf_contributions, zenodo_concepts):
    return {
        contrib[CLDF_ID]: models.ZenodoRecord(
            id=contrib[CLDF_ID],
            name=contrib[CLDF_NAME],
            concept_pk=zenodo_concepts[contrib['Concept_ID']].pk,
            description=contrib[CLDF_DESC],
            version=contrib.get('Version'),
            doi=contrib['DOI'],
            date=contrib['Date_Created'],
            date_updated=contrib['Date_Updated'],
            license=contrib['License'],
            zenodo_link=contrib['Zenodo_Link'],
            zenodo_id=contrib['Zenodo_ID'],
            zenodo_keyword=contrib['Zenodo_Keywords'],
            zenodo_type=contrib['Zenodo_Type'],
            github_link=contrib['GitHub_Link'])
        for contrib in cldf_contributions}


def iter_record_contributors(cldf_contributions, contributions, contributors):
    contributor_mapping = {}
    for contrib in cldf_contributions:
        contrib_people = []
        for name in contrib.get('Creators', ()):
            if (name, 'creator') not in contrib_people:
                contrib_people.append((name, 'creator'))
        for name in contrib.get('Contributor') or ():
            if ((name, 'creator') not in contrib_people
                and (name, 'contributor') not in contrib_people
            ):
                contrib_people.append((name, 'contributor'))
        contributor_mapping[contrib[CLDF_ID]] = contrib_people
    return (
        models.RecordContributor(
            contribution_pk=contributions[contrib_id].pk,
            contributor_pk=contributors[name].pk,
            ord=nr,
            primary=role == 'creator',
            role=role)
        for contrib_id, contrib_people in contributor_mapping.items()
        for nr, (name, role) in enumerate(contrib_people, 1))


def make_datasets(cldf_datasets, contributions):
    dataset_ords = {}
    record_dataset_count = collections.Counter()
    for cldf_dataset in sorted(cldf_datasets, key=lambda ds: ds[CLDF_ID]):
        record_id = cldf_dataset[CLDF_CONTRIB_ID]
        dataset_id = cldf_dataset[CLDF_ID]
        record_dataset_count[record_id] += 1
        dataset_ords[dataset_id] = record_dataset_count[record_id]
    # TODO: where do name and description come from
    return {
        cldf_dataset[CLDF_ID]:
        models.CLDFDataset(
            id=(id_ := cldf_dataset[CLDF_ID]),
            ord=dataset_ords[id_],
            contribution_pk=contributions[cldf_dataset[CLDF_CONTRIB_ID]].pk,
            module=cldf_dataset['Module'],
            language_count=cldf_dataset['Language_Count'],
            glottocode_count=cldf_dataset['Glottocode_Count'],
            parameter_count=cldf_dataset['Parameter_Count'],
            value_count=cldf_dataset['Value_Count'],
            form_count=cldf_dataset['Form_Count'],
            entry_count=cldf_dataset['Entry_Count'],
            example_count=cldf_dataset['Example_Count'])
        for cldf_dataset in cldf_datasets}


def get_language(languages, id_):
    if (lg := languages.get(id_)):
        return lg
    else:
        print(
            'language not found:', id_,
            '(is glottolog up-to-date?)',
            file=sys.stderr)
        return None


def iter_dataset_languages(cldf_datasetlangs, datasets, languages):
    return (
        models.DatasetLang(
            id=assoc[CLDF_ID],
            language_pk=language.pk,
            cldfdataset_pk=datasets[assoc['Dataset_ID']].pk,
            value_count=assoc['Value_Count'],
            form_count=assoc['Form_Count'],
            entry_count=assoc['Entry_Count'],
            example_count=assoc['Example_Count'])
        for assoc in cldf_datasetlangs
        if (language := get_language(languages, assoc[CLDF_LANG_ID])))


def main(args):
    if not args.cldf:
        args.log.error('missing argument: --cldf')
        return

    # read cldf data

    cldf_contributions = list(args.cldf.iter_rows(
        'ContributionTable',
        CLDF_ID, CLDF_NAME, CLDF_DESC, 'Concept_ID', 'Concept_DOI',
        'Communities', 'Contributors', 'Creators', 'DOI', 'Date_Created',
        'Date_Updated', 'GitHub_Link', 'License', 'Version', 'Zenodo_ID',
        'Zenodo_Keywords', 'Zenodo_Link', 'Zenodo_Type', 'Concept_DOI',
    ))
    cldf_languages = {
        cldf_language[CLDF_GLOTTOCODE]:
        cldf_language
        for cldf_language in args.cldf.iter_rows(
            'LanguageTable', CLDF_ID, CLDF_GLOTTOCODE)}
    cldf_datasets = list(args.cldf.iter_rows(
        'datasets.csv',
        CLDF_ID, CLDF_CONTRIB_ID, 'Module', 'Language_Count',
        'Glottocode_Count', 'Parameter_Count', 'Value_Count', 'Form_Count',
        'Entry_Count', 'Example_Count'))
    cldf_datasetlangs = list(args.cldf.iter_rows(
        'dataset-languages.csv',
        CLDF_ID, CLDF_LANG_ID, 'Dataset_ID', 'Value_Count', 'Form_Count',
        'Entry_Count', 'Example_Count'))

    # read glottolog data

    catconf = cldfcatalog.Config.from_file()
    glottolog_path = catconf.get_clone('glottolog')
    glottolog = Glottolog(glottolog_path)
    languoids = {lg.id: lg for lg in glottolog.languoids(cldf_languages)}

    # populate database

    dataset = common.Dataset(
        id='cldf_meta',
        name='CLDF Meta',
        contact='johannes_englisch@eva.mpg.de',
        domain='meta.clld.org',
        publisher_name="Max Planck Institute for Evolutionary Anthropology",
        publisher_place="Leipzig",
        publisher_url="http://www.eva.mpg.de",
        license="http://creativecommons.org/licenses/by/4.0/",
        jsondata={
            'license_icon': 'cc-by.png',
            'license_name': 'Creative Commons Attribution 4.0 International License'})
    DBSession.add(dataset)

    # TODO: communities table
    #  → Communities from contributions.csv

    zenodo_concepts = make_zenodo_concepts(cldf_contributions)
    DBSession.add_all(zenodo_concepts.values())

    contributors = make_contributors(cldf_contributions)
    DBSession.add_all(contributors.values())

    # TODO: language family information
    languages = make_languages(cldf_languages, languoids)
    DBSession.add_all(languages.values())

    DBSession.flush()

    DBSession.add(common.Editor(
        dataset_pk=dataset.pk,
        contributor_pk=contributors['Johannes Englisch'].pk))

    # :D
    DBSession.execute(sqlalchemy.text("""
        ALTER TABLE contribution DROP CONSTRAINT contribution_name_key;
    """))
    contributions = make_contributions(cldf_contributions, zenodo_concepts)
    DBSession.add_all(contributions.values())

    load_families(
        Data(),
        languages.values(),
        strict=False,
        glottolog_repos=glottolog_path)

    DBSession.flush()

    DBSession.add_all(iter_record_contributors(
        cldf_contributions, contributions, contributors))

    datasets = make_datasets(cldf_datasets, contributions)
    DBSession.add_all(datasets.values())

    DBSession.flush()

    DBSession.add_all(iter_dataset_languages(
        cldf_datasetlangs, datasets, languages))


def prime_cache(args):
    """If data needs to be denormalized for lookup, do that here.
    This procedure should be separate from the db initialization, because
    it will have to be run periodically whenever data has been updated.
    """
