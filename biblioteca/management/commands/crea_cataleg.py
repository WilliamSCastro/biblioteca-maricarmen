from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from faker import Faker
 
from biblioteca.models import *
 
availableBookLanguages = ["es_CA","es_ES", "en_GB", "fr_FR"]

class Command(BaseCommand):

    def handle(self, *args, **options):

        # LLIBRE
        for i in range(40):

            selectedLanguage = i // 10
            faker = Faker(availableBookLanguages[selectedLanguage])
            titol_llibre = faker.text(max_nb_chars=30).split(".")[0]
            llibre = Llibre(titol=titol_llibre)
            llibre.save()

        # 2 EXEMPLARS PER LLIBRE

            for j in range(2):
                exemplar = Exemplar(cataleg=llibre)
                exemplar.save()

        # 50 USUARIS
        for i in range(50):
            faker = Faker("es_ES")
            nom_usuari = faker.name()
            user = Usuari(username=nom_usuari)
            user.save()

   

