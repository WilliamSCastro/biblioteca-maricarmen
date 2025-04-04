from django.core.management.base import BaseCommand
from faker import Faker
from random import randint
from biblioteca.models import Usuari, Llibre, Exemplar, Llengua, Categoria, Pais, Centre, Cicle, Revista
from django.db import IntegrityError


class Command(BaseCommand):
    help = "Genera datos falsos para usuarios, libros, ejemplares, lenguas, centros y más"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Generando datos falsos..."))

        faker = Faker("es_ES")  # Usar Faker para Español

        # Crear Lenguas
        llengues_data = ["Catalán", "Castellano", "Inglés", "Italiano"]
        llengues = {nom: Llengua.objects.get_or_create(nom=nom)[0] for nom in llengues_data}

        # Crear Países
        paises_data = ["España", "México", "Argentina", "Italia"]
        paises = {nom: Pais.objects.get_or_create(nom=nom)[0] for nom in paises_data}

        # Crear Categorías
        categorias_data = ["Ficción", "No Ficción", "Ciencia", "Tecnología", "Historia"]
        categorias = {nom: Categoria.objects.get_or_create(nom=nom)[0] for nom in categorias_data}

        # Crear Centros
        centros_data = ["Centro A", "Centro B", "Centro C", "Centro D"]
        centros = {nom: Centre.objects.get_or_create(nom=nom)[0] for nom in centros_data}

        # Crear Ciclos
        ciclos_data = ["Ciclo 1", "Ciclo 2", "Ciclo 3"]
        ciclos = {nom: Cicle.objects.get_or_create(nom=nom)[0] for nom in ciclos_data}

        # Crear Usuarios
        usuarios = []
        for _ in range(100):  # Crear 100 usuarios
            username = faker.unique.user_name()
            email = faker.unique.email()
            user = Usuari.objects.create_user(
                username=username,
                email=email,
                password="password123",
                first_name=faker.first_name(),
                last_name=faker.last_name(),
                telefon=randint(600000000, 699999999),
                centre=faker.random_element(list(centros.values())),
                cicle=faker.random_element(list(ciclos.values()))
            )
            usuarios.append(user)

        # Crear Libros y Ejemplares
        for idioma, llengua in llengues.items():
            for _ in range(250):  # Crear 250 libros por idioma
                titol = faker.sentence(nb_words=3)
                autor = faker.name()
                isbn = faker.isbn13()
                editorial = faker.company()
                pais = faker.random_element(list(paises.values()))
                numero = randint(1, 1000)
                volums = randint(1, 5)
                pagines = randint(100, 500)
                llibre = Llibre.objects.get_or_create(
                    titol=titol,
                    autor=autor,
                    ISBN=isbn,
                    editorial=editorial,
                    pais=pais,
                    llengua=llengua,
                    numero=numero,
                    volums=volums,
                    pagines=pagines
                )[0]

                # Crear Ejemplares
                for _ in range(5):  # Crear 5 ejemplares por libro
                    registre = faker.uuid4()
                    try:
                        Exemplar.objects.get_or_create(
                            cataleg=llibre,
                            registre=registre,
                            centre=faker.random_element(list(centros.values()))
                        )
                    except IntegrityError:
                        continue  # Si ya existe el ejemplar, se genera otro

        self.stdout.write(self.style.SUCCESS("✅ Datos falsos generados con éxito 🎉"))