# Indunnova Dashboard

Dashboard de monitoreo para todas las aplicaciones de Indunnova desplegadas en Google Cloud Run.

## Características

- Vista general de todos los servicios Cloud Run (32 servicios)
- Estado de salud de cada servicio (activo/inactivo)
- Lista de repositorios GitHub (40 repositorios)
- Actualización automática cada hora via GitHub Actions
- Filtros por estado y búsqueda por nombre

## Configuración

### Secrets requeridos en GitHub

Para que la actualización automática funcione, necesitas configurar estos secrets:

1. **GCP_SA_KEY**: JSON de la cuenta de servicio de GCP con permisos de Cloud Run Viewer
2. **GH_TOKEN**: Token de GitHub con permisos de lectura de repositorios

### Crear cuenta de servicio en GCP

```bash
# Crear cuenta de servicio
gcloud iam service-accounts create dashboard-reader \
    --display-name="Dashboard Reader"

# Asignar permisos
gcloud projects add-iam-policy-binding appsindunnova \
    --member="serviceAccount:dashboard-reader@appsindunnova.iam.gserviceaccount.com" \
    --role="roles/run.viewer"

# Crear clave JSON
gcloud iam service-accounts keys create key.json \
    --iam-account=dashboard-reader@appsindunnova.iam.gserviceaccount.com
```

### Actualización manual

```bash
python scripts/update_data.py
```

## Estructura

```
├── index.html          # Página principal
├── css/styles.css      # Estilos
├── js/app.js           # Lógica frontend
├── data/               # Datos JSON (generados)
│   ├── services.json   # Servicios Cloud Run
│   ├── repos.json      # Repositorios GitHub
│   └── meta.json       # Metadatos
├── scripts/
│   └── update_data.py  # Script de actualización
└── .github/workflows/
    ├── update-data.yml # Workflow de actualización
    └── deploy-pages.yml # Workflow de despliegue
```

## Licencia

Uso interno - Indunnova
