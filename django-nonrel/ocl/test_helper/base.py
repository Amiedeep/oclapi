import random

import string

from collection.models import CollectionVersion, Collection
from concepts.models import Concept, ConceptVersion, LocalizedText
from oclapi.models import ACCESS_TYPE_EDIT, ACCESS_TYPE_VIEW
from orgs.models import Organization
from sources.models import Source, SourceVersion
from users.models import UserProfile
from mappings.models import Mapping, MappingVersion
from django.contrib.auth.models import User
from django.test import TestCase


class OclApiBaseTestCase(TestCase):
    def setUp(self):
        user = create_user()
        org_ocl = create_organization("OCL")
        classes_source = create_source(user, organization=org_ocl, name="Classes")

        create_concept(user, classes_source, concept_class="Concept Class", names=[create_localized_text("First")])
        create_concept(user, classes_source, concept_class="Concept Class", names=[create_localized_text("Second")])
        create_concept(user, classes_source, concept_class="Concept Class", names=[create_localized_text("Third")])
        create_concept(user, classes_source, concept_class="Concept Class", names=[create_localized_text("Fourth")])
        create_concept(user, classes_source, concept_class="Concept Class", names=[create_localized_text("Diagnosis")])
        create_concept(user, classes_source, concept_class="Concept Class", names=[create_localized_text("Drug")])
        create_concept(user, classes_source, concept_class="Concept Class", names=[create_localized_text("not First")])

    def tearDown(self):
        LocalizedText.objects.filter().delete()
        ConceptVersion.objects.filter().delete()
        Concept.objects.filter().delete()
        MappingVersion.objects.filter().delete()
        Mapping.objects.filter().delete()
        SourceVersion.objects.filter().delete()
        Source.objects.filter().delete()
        CollectionVersion.objects.filter().delete()
        Collection.objects.filter().delete()
        Organization.objects.filter().delete()
        UserProfile.objects.filter().delete()
        User.objects.filter().delete()


def generate_random_string(length=5):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(length))


def create_localized_text(name, locale='en', type='FULLY_SPECIFIED'):
    return LocalizedText.objects.create(name=name, locale=locale, type=type)


def create_user():
    suffix = generate_random_string()

    user = User.objects.create(
        username="test{0}".format(suffix),
        password="test{0}".format(suffix),
        email='user{0}@test.com'.format(suffix),
        first_name='Test',
        last_name='User'
    )

    UserProfile.objects.create(user=user, mnemonic='user{0}'.format(suffix))

    return user


def create_user_profile(user):
    suffix = generate_random_string()
    return UserProfile.objects.create(user=user, mnemonic='user{0}'.format(suffix))


def create_organization(name=None, mnemonic=None):
    suffix = generate_random_string()
    name = name if name else 'org{0}'.format(suffix)
    mnemonic = mnemonic if mnemonic else name
    return Organization.objects.create(name=name, mnemonic=mnemonic)


def create_source(user, validation_schema=None, organization=None, name=None):
    suffix = generate_random_string()

    source = Source(
        name=name if name else "source{0}".format(suffix),
        mnemonic=name if name else "source{0}".format(suffix),
        full_name=name if name else "Source {0}".format(suffix),
        source_type='Dictionary',
        public_access=ACCESS_TYPE_EDIT,
        default_locale='en',
        supported_locales=['en'],
        website='www.source.com',
        description='This is a test source',
        custom_validation_schema=validation_schema
    )

    if organization is not None:
        kwargs = {
            'parent_resource': organization
        }
    else:
        kwargs = {
            'parent_resource': UserProfile.objects.get(user=user)
        }

    Source.persist_new(source, user, **kwargs)

    return Source.objects.get(id=source.id)


def create_concept(user, source, names=None, mnemonic=None, descriptions=None, concept_class=None):
    suffix = generate_random_string()

    if not names:
        names = [create_localized_text("name{0}".format(suffix))]

    if not mnemonic:
        mnemonic = 'concept{0}'.format(suffix)

    if not descriptions:
        descriptions = [create_localized_text("desc{0}".format(suffix))]

    concept = Concept(
        mnemonic=mnemonic,
        updated_by=user,
        datatype="None",
        concept_class = concept_class if concept_class else 'First',
        names=names,
        descriptions=descriptions,
    )

    if source is not None:
        kwargs = {
            'parent_resource': source,
        }
        errors = Concept.persist_new(concept, user, **kwargs)
    else:
        errors = Concept.persist_new(concept, user)

    return (concept, errors)

def create_mapping(user, source, from_concept, to_concept, map_type="Same As"):
    mapping = Mapping(
        created_by=user,
        updated_by=user,
        parent=source,
        map_type=map_type,
        from_concept=from_concept,
        to_concept=to_concept,
        public_access=ACCESS_TYPE_VIEW,
    )

    kwargs = {
        'parent_resource': source,
    }

    Mapping.persist_new(mapping, user, **kwargs)

    return Mapping.objects.get(id=mapping.id)