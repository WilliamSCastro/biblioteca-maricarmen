from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from django.contrib.auth.hashers import make_password
from django.core.validators import RegexValidator

class Centre(models.Model):
    nom = models.CharField(max_length=200)

    def __str__(self):
        return self.nom

class Categoria(models.Model):
    class Meta:
        verbose_name_plural = "Categories"
    nom = models.CharField(max_length=100)
    parent = models.ForeignKey('self',on_delete=models.CASCADE,null=True,blank=True)
    def __str__(self):
        return self.nom

class Pais(models.Model):
    class Meta:
        verbose_name_plural = "Països"
    nom = models.CharField(max_length=200)
    def __str__(self):
        return self.nom

class Llengua(models.Model):
    class Meta:
        verbose_name_plural = "Llengües"
    nom = models.CharField(max_length=200)
    def __str__(self):
        return self.nom

class Cataleg(models.Model):
    titol = models.CharField(max_length=200)
    titol_original = models.CharField(max_length=200, blank=True, null=True)
    autor = models.CharField(max_length=200, blank=True, null=True)
    CDU = models.CharField(max_length=40, blank=True, null=True)
    signatura = models.CharField(max_length=40, blank=True, null=True)
    data_edicio = models.DateField(null=True,blank=True)
    resum = models.TextField(blank=True,null=True)
    anotacions = models.TextField(blank=True,null=True)
    mides = models.CharField(max_length=100,null=True,blank=True)
    tags = models.ManyToManyField(Categoria,blank=True)
    def __str__(self):
        return self.titol

class Llibre(Cataleg):
    ISBN = models.CharField(max_length=13, blank=True, null=True)
    editorial = models.CharField(max_length=100, blank=True, null=True)
    colleccio = models.CharField(max_length=100, blank=True, null=True)
    lloc = models.CharField(max_length=100, blank=True, null=True)
    pais = models.ForeignKey(Pais, on_delete=models.SET_NULL, blank=True, null=True)
    llengua = models.ForeignKey(Llengua, on_delete=models.SET_NULL, blank=True, null=True)
    numero = models.IntegerField(null=True,blank=True)
    volums = models.IntegerField(null=True,blank=True)
    pagines = models.IntegerField(blank=True,null=True)
    info_url = models.CharField(max_length=200,blank=True,null=True)
    preview_url = models.CharField(max_length=200,blank=True,null=True)
    thumbnail_url = models.CharField(max_length=200,blank=True,null=True)

class Revista(Cataleg):
    class Meta:
        verbose_name_plural = "Revistes"
    ISSN = models.CharField(max_length=13, blank=True, null=True)
    editorial = models.CharField(max_length=100, blank=True, null=True)
    lloc = models.CharField(max_length=100, blank=True, null=True)
    pais = models.ForeignKey(Pais, on_delete=models.SET_NULL, blank=True, null=True)
    llengua = models.ForeignKey(Llengua, on_delete=models.SET_NULL, blank=True, null=True)
    numero = models.IntegerField(null=True,blank=True)
    volums = models.IntegerField(null=True,blank=True)
    pagines = models.IntegerField(blank=True,null=True)

class CD(Cataleg):
    discografica = models.CharField(max_length=100)
    estil = models.CharField(max_length=100)
    duracio = models.TimeField()

class DVD(Cataleg):
    productora = models.CharField(max_length=100)
    duracio = models.TimeField()

class BR(Cataleg):
    productora = models.CharField(max_length=100)
    duracio = models.TimeField()

class Dispositiu(Cataleg):
    marca = models.CharField(max_length=100)
    model = models.CharField(max_length=100,null=True,blank=True)

class Exemplar(models.Model):
    cataleg = models.ForeignKey(Cataleg, on_delete=models.CASCADE)
    registre = models.CharField(max_length=20, unique=True, editable=False)  # Único y no editable
    exclos_prestec = models.BooleanField(default=False) 
    baixa = models.BooleanField(default=False)
    centre = models.ForeignKey(Centre, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['cataleg', 'id'], name='unique_cataleg_exemplar')
        ]
    
    def save(self, *args, **kwargs):
        if not self.registre:  # Solo generar si no existe
            year = now().year
            last_exemplar = Exemplar.objects.filter(registre__startswith=f"EX-{year}").order_by('id').last()
            if last_exemplar:
                last_number = int(last_exemplar.registre.split('-')[-1])
            else:
                last_number = 0
            self.registre = f"EX-{year}-{last_number + 1:06d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"REG:{self.registre} - {self.cataleg.titol}"
    
class Imatge(models.Model):
    cataleg = models.ForeignKey(Cataleg, on_delete=models.CASCADE)
    imatge = models.ImageField(upload_to='imatges/')

# Usuaris
class Grup(models.Model):
    nom = models.CharField(max_length=200)

    def __str__(self):
        return self.nom
    
    
class Usuari(AbstractUser):
    centre = models.ForeignKey(Centre,on_delete=models.SET_NULL,null=True,blank=True)
    grup = models.ForeignKey(Grup,on_delete=models.SET_NULL,null=True,blank=True)
    telefon =  models.CharField(max_length=9,validators=[RegexValidator(regex=r'^\d+$', message="Només es permeten números.")],blank=True,null=True)

    imatge = models.ImageField(upload_to='usuaris/',null=True,blank=True)
    auth_token = models.CharField(max_length=32,blank=True,null=True)

class Reserva(models.Model):
    class Meta:
        verbose_name_plural = "Reserves"
    usuari = models.ForeignKey(Usuari, on_delete=models.CASCADE)
    exemplar = models.ForeignKey(Exemplar, on_delete=models.CASCADE)
    data = models.DateField(auto_now_add=True)

class Prestec(models.Model):
    class Meta:
        verbose_name_plural = "Préstecs"
    usuari = models.ForeignKey(Usuari, on_delete=models.CASCADE)
    exemplar = models.ForeignKey(Exemplar, on_delete=models.CASCADE)
    data_prestec = models.DateField(auto_now_add=True)
    data_retorn = models.DateField(null=True, blank=True)
    anotacions = models.TextField(blank=True,null=True)
    def __str__(self):
        return str(self.exemplar)

class Peticio(models.Model):
    class Meta:
        verbose_name_plural = "Peticions"
    usuari = models.ForeignKey(Usuari, on_delete=models.CASCADE)
    titol = models.CharField(max_length=200)
    descripcio = models.TextField()
    data = models.DateField(auto_now_add=True)

class Log(models.Model):
    TIPO_LOG = (
        ('INFO', 'Información'),
        ('WARNING', 'Advertencia'),
        ('ERROR', 'Error'),
        ('FATAL', 'Fatal'),
    )
    usuari = models.CharField(max_length=100, null=True, blank=True)
    accio = models.CharField(max_length=100)
    data_accio = models.DateTimeField(auto_now_add=True)
    tipus = models.CharField(max_length=10, choices=TIPO_LOG, default="")

    def __str__(self):
        return f"{self.accio} - {self.tipus}"
