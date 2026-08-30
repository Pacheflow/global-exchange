from django.db import migrations


def crear_categorias(apps, schema_editor):
    """Crea las categorías iniciales utilizadas para segmentar clientes."""

    CategoriaCliente = apps.get_model("clientes", "CategoriaCliente")

    categorias = [
        ("Minorista", "Cliente minorista"),
        ("Corporativo", "Cliente corporativo"),
        ("VIP", "Cliente VIP"),
    ]

    for nombre, descripcion in categorias:
        CategoriaCliente.objects.get_or_create(
            nombre=nombre,
            defaults={"descripcion": descripcion},
        )


class Migration(migrations.Migration):

    dependencies = [
        ("clientes", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            crear_categorias,
            migrations.RunPython.noop,
        ),
    ]