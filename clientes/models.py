from django.db import models


class CategoriaCliente(models.Model):
    """Representa una categoría comercial asignable a los clientes."""

    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


class Cliente(models.Model):
    """Representa un cliente de Global Exchange.

    Guarda información como tipo de persona, documento,
    estado y categoría comercial.
    """

    TIPOS_PERSONA = [
        ('FISICA', 'Persona Física'),
        ('JURIDICA', 'Persona Jurídica'),
    ]

    ESTADOS_CLIENTE = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
    ]

    nombre_razon_social = models.CharField(max_length=150)

    tipo_persona = models.CharField(
        max_length=10,
        choices=TIPOS_PERSONA
    )

    documento = models.CharField(
        max_length=30,
        unique=True
    )

    estado = models.CharField(
        max_length=10,
        choices=ESTADOS_CLIENTE,
        default='ACTIVO'
    )

    categoria = models.ForeignKey(
        CategoriaCliente,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre_razon_social

    def activar(self):
        """Cambia el estado del cliente a ACTIVO."""
        self.estado = 'ACTIVO'
        self.save()

    def dar_de_baja(self):
        """Cambia el estado del cliente a INACTIVO sin eliminarlo."""
        self.estado = 'INACTIVO'
        self.save()