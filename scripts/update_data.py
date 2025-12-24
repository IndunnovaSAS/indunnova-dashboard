#!/usr/bin/env python3
"""
Script para actualizar los datos del dashboard de Indunnova.
Obtiene información de Cloud Run y GitHub para generar los archivos JSON.
"""

import json
import subprocess
import os
from datetime import datetime

# Mapeo de servicios Cloud Run a repositorios
SERVICE_TO_REPO = {
    'arcopack-erp': 'Arcopack',
    'carnes-sebastian': 'carnesdelsebastian',
    'carnes-sebastian-staging': 'carnesdelsebastian',
    'carnesdelsebastian': 'carnesdelsebastian',
    'carnesdelsebastian-staging': 'carnesdelsebastian',
    'codeta-crm': 'CODETA',
    'colsegur': 'Colsegur',
    'creaciones-apice': 'CreacionesApice',
    'crm-contenedores': 'ObrajeCRM',
    'crm-ecourmet': 'EcourmetV2',
    'crm-gyt': 'GYT',
    'crm-komsa': 'KOMSA',
    'formas-futuro': 'FormasFuturo',
    'fundiciones-medellin': 'FundicionesMedellin',
    'gestion-proveedores-isa': 'GestionProveedoresISA',
    'hemisferio-erp': 'Hemisferio',
    'huella-carbono': 'HuellaCarbono',
    'jardin-botanico': 'JardinBotanico',
    'logiempresas': 'Logiempresas',
    'mentes-estrategicas': 'mentes_estrategicas',
    'moldes-mecanizados-app': 'MoldesyMecanizados',
    'mouse-digital': 'MouseDigital',
    'novapcr-app': 'NOVAPCR',
    'plasticos-ambientales': 'PlasticosAmbientales',
    'rgd-aire': 'RGDAire',
    'seyca': 'seyca_produccion',
    'seyca-produccion': 'seyca_produccion',
    'tersasoft': 'tersaSoft',
    'vid-comunicaciones': 'VID',
}

GITHUB_ORG = 'mbrt26'

def run_command(cmd):
    """Ejecuta un comando y retorna su salida."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        return result.stdout.strip()
    except Exception as e:
        print(f"Error ejecutando comando: {e}")
        return ""

def get_cloud_run_services():
    """Obtiene la lista de servicios de Cloud Run."""
    cmd = 'gcloud run services list --format="json" 2>/dev/null'
    output = run_command(cmd)

    if not output:
        return []

    try:
        data = json.loads(output)
        services = []

        for svc in data:
            name = svc['metadata']['name']
            url = svc['status'].get('url', 'N/A')

            # Obtener estado
            conditions = svc['status'].get('conditions', [])
            status = 'Unknown'
            for c in conditions:
                if c['type'] == 'Ready':
                    status = c['status']
                    break

            # Obtener región
            region = svc['metadata'].get('labels', {}).get('cloud.googleapis.com/location', 'us-central1')

            # Mapear a repositorio
            repo_name = SERVICE_TO_REPO.get(name)
            repo_url = f"https://github.com/{GITHUB_ORG}/{repo_name}" if repo_name else None

            services.append({
                'name': name,
                'url': url,
                'status': status,
                'region': region,
                'repo': repo_url,
                'repoName': repo_name
            })

        return services
    except json.JSONDecodeError as e:
        print(f"Error parseando JSON de Cloud Run: {e}")
        return []

def get_github_repos():
    """Obtiene la lista de repositorios de GitHub."""
    cmd = 'gh repo list --limit 100 --json name,url,updatedAt,description 2>/dev/null'
    output = run_command(cmd)

    if not output:
        return []

    try:
        data = json.loads(output)
        repos = []

        # Crear mapeo inverso para encontrar servicios Cloud Run
        repo_to_service = {v: k for k, v in SERVICE_TO_REPO.items()}

        for repo in data:
            cloud_run_service = repo_to_service.get(repo['name'])

            repos.append({
                'name': repo['name'],
                'url': repo['url'],
                'description': repo.get('description', ''),
                'updatedAt': repo.get('updatedAt', ''),
                'cloudRunService': cloud_run_service
            })

        return repos
    except json.JSONDecodeError as e:
        print(f"Error parseando JSON de GitHub: {e}")
        return []

def main():
    """Función principal."""
    # Determinar directorio de datos
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(script_dir), 'data')

    # Crear directorio si no existe
    os.makedirs(data_dir, exist_ok=True)

    print("Obteniendo servicios de Cloud Run...")
    services = get_cloud_run_services()
    print(f"  Encontrados {len(services)} servicios")

    print("Obteniendo repositorios de GitHub...")
    repos = get_github_repos()
    print(f"  Encontrados {len(repos)} repositorios")

    # Guardar datos
    services_path = os.path.join(data_dir, 'services.json')
    repos_path = os.path.join(data_dir, 'repos.json')
    meta_path = os.path.join(data_dir, 'meta.json')

    with open(services_path, 'w') as f:
        json.dump(services, f, indent=2)
    print(f"  Guardado: {services_path}")

    with open(repos_path, 'w') as f:
        json.dump(repos, f, indent=2)
    print(f"  Guardado: {repos_path}")

    # Metadatos
    meta = {
        'lastUpdate': datetime.utcnow().isoformat() + 'Z',
        'project': 'appsindunnova',
        'totalServices': len(services),
        'totalRepos': len(repos),
        'healthyServices': len([s for s in services if s['status'] == 'True']),
        'unhealthyServices': len([s for s in services if s['status'] != 'True'])
    }

    with open(meta_path, 'w') as f:
        json.dump(meta, f, indent=2)
    print(f"  Guardado: {meta_path}")

    print("\nActualización completada!")

if __name__ == '__main__':
    main()
