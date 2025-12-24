// Global data stores
let servicesData = [];
let reposData = [];

// Load data on page load
document.addEventListener('DOMContentLoaded', loadData);

async function loadData() {
    try {
        // Load services data
        const servicesResponse = await fetch('data/services.json');
        servicesData = await servicesResponse.json();

        // Load repos data
        const reposResponse = await fetch('data/repos.json');
        reposData = await reposResponse.json();

        // Update last update time
        const metaResponse = await fetch('data/meta.json');
        const meta = await metaResponse.json();
        document.getElementById('lastUpdate').textContent = `Última actualización: ${formatDate(meta.lastUpdate)}`;

        // Render everything
        updateSummary();
        renderServices();
        renderRepos();
    } catch (error) {
        console.error('Error loading data:', error);
        document.getElementById('servicesGrid').innerHTML = '<div class="loading">Error al cargar datos. Verifique que los archivos JSON existen.</div>';
        document.getElementById('reposGrid').innerHTML = '<div class="loading">Error al cargar datos.</div>';
    }
}

function updateSummary() {
    const totalServices = servicesData.length;
    const healthyServices = servicesData.filter(s => s.status === 'True').length;
    const unhealthyServices = totalServices - healthyServices;
    const totalRepos = reposData.length;

    document.getElementById('totalServices').textContent = totalServices;
    document.getElementById('healthyServices').textContent = healthyServices;
    document.getElementById('unhealthyServices').textContent = unhealthyServices;
    document.getElementById('totalRepos').textContent = totalRepos;
}

function renderServices() {
    const grid = document.getElementById('servicesGrid');
    const statusFilter = document.getElementById('statusFilter').value;
    const searchFilter = document.getElementById('searchFilter').value.toLowerCase();

    let filtered = servicesData;

    // Apply status filter
    if (statusFilter === 'healthy') {
        filtered = filtered.filter(s => s.status === 'True');
    } else if (statusFilter === 'unhealthy') {
        filtered = filtered.filter(s => s.status !== 'True');
    }

    // Apply search filter
    if (searchFilter) {
        filtered = filtered.filter(s => s.name.toLowerCase().includes(searchFilter));
    }

    if (filtered.length === 0) {
        grid.innerHTML = '<div class="loading">No se encontraron servicios.</div>';
        return;
    }

    grid.innerHTML = filtered.map(service => `
        <div class="service-card ${service.status === 'True' ? '' : 'unhealthy'}">
            <div class="service-header">
                <span class="service-name">${service.name}</span>
                <span class="service-status ${service.status === 'True' ? 'healthy' : 'unhealthy'}">
                    ${service.status === 'True' ? '● Activo' : '● Inactivo'}
                </span>
            </div>
            <div class="service-url">
                <a href="${service.url}" target="_blank" rel="noopener">${service.url}</a>
            </div>
            <div class="service-meta">
                <span>📍 ${service.region}</span>
                ${service.repo ? `<span>📦 <a href="${service.repo}" target="_blank" style="color: inherit;">${extractRepoName(service.repo)}</a></span>` : ''}
            </div>
        </div>
    `).join('');
}

function renderRepos() {
    const grid = document.getElementById('reposGrid');

    if (reposData.length === 0) {
        grid.innerHTML = '<div class="loading">No se encontraron repositorios.</div>';
        return;
    }

    grid.innerHTML = reposData.map(repo => `
        <div class="repo-card">
            <div class="repo-header">
                <span class="repo-name">
                    <a href="${repo.url}" target="_blank" rel="noopener">${repo.name}</a>
                </span>
            </div>
            <div class="repo-description">${repo.description || 'Sin descripción'}</div>
            <div class="repo-meta">
                <span>🕐 ${formatDate(repo.updatedAt)}</span>
                ${repo.cloudRunService ? `<span>☁️ ${repo.cloudRunService}</span>` : ''}
            </div>
        </div>
    `).join('');
}

function filterServices() {
    renderServices();
}

function formatDate(dateString) {
    if (!dateString) return '--';
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function extractRepoName(url) {
    if (!url) return '';
    const parts = url.split('/');
    return parts[parts.length - 1] || parts[parts.length - 2];
}
