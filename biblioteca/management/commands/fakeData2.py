from django.core.management.base import BaseCommand
from faker import Faker
from random import randint, choice
import random
from datetime import timedelta, datetime
from biblioteca.models import (
    Llibre, Revista, CD, DVD, BR, Dispositiu, Exemplar,
    Llengua, Categoria, Pais, Centre
)
from django.db import IntegrityError
from django.utils import timezone


class Command(BaseCommand):
    help = "Genera dades falses per a catàleg i exemplars, amb 5-10 ítems per autor"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("📚 Generant catàleg fals..."))

        fake = Faker("es_ES")

        llengues = [Llengua.objects.get_or_create(nom=nom)[0] for nom in ["Català", "Castellà", "Anglès"]]
        paisos = [Pais.objects.get_or_create(nom=nom)[0] for nom in ["Espanya", "França", "Estats Units"]]
        categories = [Categoria.objects.get_or_create(nom=nom)[0] for nom in ["Ficció", "Tecnologia", "Història"]]
        centres = list(Centre.objects.get_or_create(nom=nom)[0] for nom in ["Centre A", "Centre B", "Centre C", "Centre D", "Centre E"])
        
        def assign_tags(instance):
            instance.save()
            instance.tags.set([choice(categories)])
        def generar_registre(anyo=None):
            # Año actual si no se especifica
            if not anyo:
                anyo = datetime.now().year

            numero = random.randint(0, 999999)
            numero_formateado = f"{numero:06d}"  # siempre 6 dígitos con ceros delante
            return f"EX-{anyo}-{numero_formateado}"

        def create_exemplars(obj):
            for _ in range(randint(2, 5)):
                try:
                    Exemplar.objects.get_or_create(
                        cataleg=obj,
                        registre = generar_registre(),
                        centre=choice(centres)
                    )
                except IntegrityError:
                    continue

        # 🔁 Generamos 10 autores
        autors = [fake.name() for _ in range(100)]

        for autor in autors:
            num_obres = randint(5, 10)
            for _ in range(num_obres):
                tipus = choice(["llibre", "revista", "cd", "dvd", "br", "dispositiu"])

                if tipus == "llibre":
                    obj = Llibre.objects.create(
                        titol=fake.sentence(nb_words=3),
                        titol_original=fake.sentence(nb_words=3),
                        autor=autor,
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

                elif tipus == "revista":
                    obj = Revista.objects.create(
                        titol=fake.catch_phrase(),
                        titol_original=None,
                        autor=autor,
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

                elif tipus == "cd":
                    obj = CD.objects.create(
                        titol=fake.catch_phrase(),
                        autor=autor,
                        discografica=fake.company(),
                        estil=fake.word(),
                        duracio=fake.time_object(),
                        signatura=f"{randint(100,999)}.CD",
                    )

                elif tipus == "dvd":
                    obj = DVD.objects.create(
                        titol=fake.catch_phrase(),
                        autor=autor,
                        productora=fake.company(),
                        duracio=fake.time_object(),
                        signatura=f"{randint(100,999)}.DVD",
                    )

                elif tipus == "br":
                    obj = BR.objects.create(
                        titol=fake.catch_phrase(),
                        autor=autor,
                        productora=fake.company(),
                        duracio=fake.time_object(),
                        signatura=f"{randint(100,999)}.BR",
                    )

                elif tipus == "dispositiu":
                    obj = Dispositiu.objects.create(
                        titol=f"Dispositiu {fake.word()}",
                        autor=autor,
                        marca=fake.company(),
                        model=fake.word(),
                        signatura=f"{randint(100,999)}.D",
                    )

                assign_tags(obj)
                create_exemplars(obj)

        self.stdout.write(self.style.SUCCESS("✅ Catàleg fals generat amb èxit! 🎉"))
