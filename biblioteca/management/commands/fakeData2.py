from django.core.management.base import BaseCommand
from faker import Faker
from random import randint, choice
from datetime import timedelta, datetime
from biblioteca.models import (
    Llibre, Revista, CD, DVD, BR, Dispositiu, Exemplar,
    Llengua, Categoria, Pais, Centre
)
from django.db import IntegrityError
from django.utils import timezone


class Command(BaseCommand):
    help = "Genera dades falses per a catàleg i exemplars"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("📚 Generant catàleg fals..."))

        fake = Faker("es_ES")

        llengues = [Llengua.objects.get_or_create(nom=nom)[0] for nom in ["Català", "Castellà", "Anglès"]]
        paisos = [Pais.objects.get_or_create(nom=nom)[0] for nom in ["Espanya", "França", "Estats Units"]]
        categories = [Categoria.objects.get_or_create(nom=nom)[0] for nom in ["Ficció", "Tecnologia", "Història"]]
        centres = list(Centre.objects.all())

        def assign_tags(instance):
            instance.save()
            instance.tags.set([choice(categories)])

        def create_exemplars(obj):
            for _ in range(randint(2, 5)):
                try:
                    Exemplar.objects.get_or_create(
                        cataleg=obj,
                        registre=fake.uuid4(),
                        centre=choice(centres)
                    )
                except IntegrityError:
                    continue

        # 📘 LLIBRES
        for _ in range(20):
            llibre = Llibre.objects.create(
                titol=fake.sentence(nb_words=3),
                titol_original=fake.sentence(nb_words=3),
                autor=fake.name(),
                ISBN=fake.isbn13().replace("-", ""),
                editorial=fake.company(),
                lloc=fake.city(),
                pais=choice(paisos),
                llengua=choice(llengues),
                numero=randint(1, 100),
                volums=randint(1, 3),
                pagines=randint(100, 500),
                signatura=f"{randint(100,999)}.{chr(randint(65,90))}",
                data_edicio=fake.date_between(start_date='-10y', end_date='today'),
                resum=fake.text(200),
                anotacions=fake.text(100),
                mides=f"{randint(20,30)}cm",
            )
            assign_tags(llibre)
            create_exemplars(llibre)

        # 📙 REVISTES
        for _ in range(10):
            revista = Revista.objects.create(
                titol=fake.catch_phrase(),
                titol_original=None,
                autor=fake.name(),
                ISSN=str(randint(1000000000000, 9999999999999)),
                editorial=fake.company(),
                lloc=fake.city(),
                pais=choice(paisos),
                llengua=choice(llengues),
                numero=randint(1, 50),
                volums=randint(1, 5),
                pagines=randint(50, 150),
                signatura=f"{randint(100,999)}.{chr(randint(65,90))}",
                data_edicio=fake.date_between(start_date='-5y', end_date='today'),
                resum=fake.text(200),
                anotacions=fake.text(100),
                mides=f"{randint(20,30)}cm",
            )
            assign_tags(revista)
            create_exemplars(revista)

        # 💿 CDs
        for _ in range(10):
            cd = CD.objects.create(
                titol=fake.catch_phrase(),
                autor=fake.name(),
                discografica=fake.company(),
                estil=fake.word(),
                duracio=fake.time_object(),
                signatura=f"{randint(100,999)}.CD",
            )
            assign_tags(cd)
            create_exemplars(cd)

        # 📀 DVDs
        for _ in range(10):
            dvd = DVD.objects.create(
                titol=fake.catch_phrase(),
                autor=fake.name(),
                productora=fake.company(),
                duracio=fake.time_object(),
                signatura=f"{randint(100,999)}.DVD",
            )
            assign_tags(dvd)
            create_exemplars(dvd)

        # 🔵 BR (Blu-Ray)
        for _ in range(10):
            br = BR.objects.create(
                titol=fake.catch_phrase(),
                autor=fake.name(),
                productora=fake.company(),
                duracio=fake.time_object(),
                signatura=f"{randint(100,999)}.BR",
            )
            assign_tags(br)
            create_exemplars(br)

        # 💻 Dispositius
        for _ in range(10):
            dispositiu = Dispositiu.objects.create(
                titol=f"Dispositiu {fake.word()}",
                autor=None,
                marca=fake.company(),
                model=fake.word(),
                signatura=f"{randint(100,999)}.D",
            )
            assign_tags(dispositiu)
            create_exemplars(dispositiu)

        self.stdout.write(self.style.SUCCESS("✅ Catàleg fals generat amb èxit! 🎉"))