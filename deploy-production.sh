#!/bin/bash

# Salir si algo falla
set -e

echo "Eliminando carpeta static/..."
rm -rf static/

echo "Ejecutando deploy-react.sh..."
./deploy-react.sh

echo "Recolectando archivos estáticos..."
./manage.py collectstatic

echo "Reiniciando Apache..."
sudo systemctl restart apache2

echo "Despliegue completado exitosamente."
