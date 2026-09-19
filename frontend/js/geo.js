/* Geo Locator Map & Navigation Engine — Interactive Leaflet Integration */

let geoMapInstance = null;
let geoMarkers = {}; 
let geoPinsData = [];
let geoUserMarker = null; 
let geoUserLocation = null; 
let geoCurrentRouteLayer = null; 
let geoMapInitialized = false;

const DEFAULT_MAP_CENTER = { lat: 13.0827, lng: 80.2707 }; // Default India view
const DEFAULT_MAP_ZOOM = 12;

async function renderGeoLocatorPage() {
  // 1. Initialize Map if not already created
  if (!geoMapInitialized) {
    initGeoMap();
  }

  // Multi-phase invalidateSize to ensure map tiles render properly when tab turns visible
  [50, 150, 350, 600].forEach(delay => {
    setTimeout(() => {
      if (geoMapInstance) {
        geoMapInstance.invalidateSize();
      }
    }, delay);
  });

  // 2. Fetch pins from Backend API
  await loadGeoPins();
}

async function loadGeoPins(lat = null, lng = null) {
  let endpoint = '/geo/pins';
  if (lat !== null && lng !== null) {
    endpoint += `?lat=${lat}&lng=${lng}`;
  }

  setGeoLoading(true);

  try {
    const res = await apiRequest(endpoint, { method: 'GET' });
    if (res && Array.isArray(res)) {
      geoPinsData = res;
      renderGeoMarkers();
      updateGeoPinsList();
    } else {
      showGeoNotification("Failed to load channel agency locations.", true);
    }
  } catch (err) {
    console.error("Geo pins error:", err);
    showGeoNotification(err.message || "Error connecting to location server.", true);
  } finally {
    setGeoLoading(false);
  }
}

function initGeoMap() {
  const mapContainer = document.getElementById("map-container");
  if (!mapContainer) return;

  if (typeof L === "undefined") {
    showGeoNotification("Leaflet Map SDK failed to load.", true);
    return;
  }

  try {
    geoMapInstance = L.map("map-container", {
      zoomControl: false,
      attributionControl: false
    }).setView([DEFAULT_MAP_CENTER.lat, DEFAULT_MAP_CENTER.lng], DEFAULT_MAP_ZOOM);

    // Highly reliable CartoDB Voyager map tiles
    L.tileLayer("https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png", {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
      subdomains: 'abcd',
      maxZoom: 19
    }).addTo(geoMapInstance);

    L.control.zoom({ position: "topright" }).addTo(geoMapInstance);

    setupGeoEventListeners();
    geoMapInitialized = true;

    // Recalibrate tile positions
    setTimeout(() => {
      if (geoMapInstance) geoMapInstance.invalidateSize();
    }, 150);

  } catch (err) {
    console.error("Leaflet init error:", err);
  }
}

function setupGeoEventListeners() {
  const searchForm = document.getElementById("search-form");
  const myLocationBtn = document.getElementById("my-location-btn");
  const clearRouteBtn = document.getElementById("clear-route-btn");

  if (searchForm) {
    searchForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const input = document.getElementById("search-input");
      if (input && input.value.trim()) {
        searchGeoLocation(input.value.trim());
      }
    });
  }

  if (myLocationBtn) {
    myLocationBtn.addEventListener("click", getGeoUserLocation);
  }

  if (clearRouteBtn) {
    clearRouteBtn.addEventListener("click", clearGeoRoute);
  }
}

function renderGeoMarkers() {
  if (!geoMapInstance) return;

  geoPinsData.forEach((pin) => {
    if (!geoMarkers[pin.id]) {
      createGeoMarker(pin);
    }
  });
}

function createGeoMarker(pin) {
  const markerIcon = L.divIcon({
    html: `<div style="background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%); width: 28px; height: 28px; border-radius: 50%; border: 3px solid #FFFFFF; box-shadow: 0 4px 14px rgba(79,70,229,0.45); display: flex; align-items: center; justify-content: center; color: #FFFFFF; font-size: 12px; font-weight: 700;">📍</div>`,
    className: "",
    iconSize: [28, 28],
    iconAnchor: [14, 14],
  });

  const marker = L.marker([pin.lat, pin.lng], { icon: markerIcon }).addTo(geoMapInstance);

  const tooltipContent = `
    <div style="font-weight: 700; font-size: 13px; color: #0F172A;">${pin.name}</div>
    <div style="font-size: 11px; color: #64748B;">${pin.description || ''}</div>
  `;

  marker.bindTooltip(tooltipContent, {
    direction: "top",
    offset: [0, -10],
    opacity: 0.95,
    sticky: true
  });

  const popupContent = `
    <div class="popup-content">
      <h4>${pin.name}</h4>
      <p>${pin.description || ''}</p>
      ${pin.phone ? `<p style="font-size: 0.8rem; margin-bottom: 8px;"><strong>Phone:</strong> ${pin.phone}</p>` : ''}
      <div class="popup-actions">
        <button class="popup-btn" onclick="navigateToPin('${pin.id}')">Navigate</button>
      </div>
    </div>
  `;

  marker.bindPopup(popupContent);
  geoMarkers[pin.id] = marker;
}

function updateGeoPinsList() {
  const listEl = document.getElementById("pins-list");
  const countEl = document.getElementById("pin-count");
  if (!listEl) return;

  listEl.innerHTML = "";

  const displayPins = geoPinsData.slice(0, 5);
  if (countEl) countEl.textContent = displayPins.length;

  displayPins.forEach((pin) => {
    const li = document.createElement("li");
    li.className = "pin-item";

    let distHtml = "";
    if (pin.distance !== null && pin.distance !== undefined) {
      distHtml = `<span class="pin-dist">${pin.distance.toFixed(1)} km</span>`;
    }

    li.innerHTML = `
      <div class="pin-header">
        <span class="pin-title">${pin.name}</span>
        ${distHtml}
      </div>
      <div class="pin-actions">
        <button class="pin-btn" onclick="focusGeoPin('${pin.id}')">View</button>
        <button class="pin-btn nav" onclick="navigateToPin('${pin.id}')">Navigate</button>
      </div>
    `;
    listEl.appendChild(li);
  });
}

window.focusGeoPin = function (pinId) {
  const pin = geoPinsData.find((p) => p.id === pinId);
  if (pin && geoMarkers[pinId] && geoMapInstance) {
    geoMapInstance.flyTo([pin.lat, pin.lng], 15);
    geoMarkers[pinId].openPopup();
  }
};

window.navigateToPin = async function (pinId) {
  if (!geoUserLocation) {
    showGeoNotification("Fetching your current location for navigation...");
    if (!navigator.geolocation) {
      showGeoNotification("Geolocation is not supported by your browser.", true);
      return;
    }

    setGeoLoading(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setGeoLoading(false);
        geoUserLocation = { lat: pos.coords.latitude, lng: pos.coords.longitude };
        updateGeoUserMarker();
        calculateGeoRouteTo(pinId);
      },
      (err) => {
        setGeoLoading(false);
        showGeoNotification("Failed to get your location for navigation.", true);
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
    return;
  }

  calculateGeoRouteTo(pinId);
};

async function calculateGeoRouteTo(pinId) {
  const destination = geoPinsData.find((p) => p.id === pinId);
  if (!destination || !geoUserLocation) return;

  setGeoLoading(true);
  clearGeoRoute();

  try {
    const endpoint = `/geo/route?start_lng=${geoUserLocation.lng}&start_lat=${geoUserLocation.lat}&end_lng=${destination.lng}&end_lat=${destination.lat}`;
    const data = await apiRequest(endpoint, { method: 'GET' });

    if (data && data.code === "Ok" && data.routes && data.routes.length > 0) {
      const route = data.routes[0];
      const coordinates = route.geometry.coordinates.map((coord) => [coord[1], coord[0]]);

      geoCurrentRouteLayer = L.polyline(coordinates, {
        color: "#4F46E5",
        weight: 6,
        opacity: 0.85,
        lineJoin: "round",
      }).addTo(geoMapInstance);

      geoMapInstance.fitBounds(geoCurrentRouteLayer.getBounds(), { padding: [50, 50] });

      const distKm = (route.distance / 1000).toFixed(1);
      const timeMin = Math.round(route.duration / 60);

      const navInfoPanel = document.getElementById("nav-info-panel");
      const routeDetailsEl = document.getElementById("route-details");

      if (routeDetailsEl) {
        routeDetailsEl.innerHTML = `
          <div><strong>Destination:</strong> ${destination.name}</div>
          <div><strong>Distance:</strong> ${distKm} km</div>
          <div><strong>Est. Driving Time:</strong> ${timeMin} mins</div>
        `;
      }
      if (navInfoPanel) navInfoPanel.classList.remove("hidden");
    } else {
      showGeoNotification("Unable to calculate driving route.", true);
    }
  } catch (err) {
    console.error("Route calculation error:", err);
    showGeoNotification("Routing service error.", true);
  } finally {
    setGeoLoading(false);
  }
}

function clearGeoRoute() {
  if (geoCurrentRouteLayer && geoMapInstance) {
    geoMapInstance.removeLayer(geoCurrentRouteLayer);
    geoCurrentRouteLayer = null;
  }
  const navInfoPanel = document.getElementById("nav-info-panel");
  const routeDetailsEl = document.getElementById("route-details");
  if (navInfoPanel) navInfoPanel.classList.add("hidden");
  if (routeDetailsEl) routeDetailsEl.innerHTML = "";
}

async function searchGeoLocation(query) {
  setGeoLoading(true);
  try {
    const endpoint = `/geo/search?q=${encodeURIComponent(query)}`;
    const data = await apiRequest(endpoint, { method: 'GET' });

    if (data && Array.isArray(data) && data.length > 0) {
      const result = data[0];
      const lat = parseFloat(result.lat);
      const lng = parseFloat(result.lon);

      if (geoMapInstance) {
        geoMapInstance.flyTo([lat, lng], 14);
        showGeoNotification(`Centered map on ${result.display_name.split(',')[0]}`);
      }
    } else {
      showGeoNotification("No location results found for search query.", true);
    }
  } catch (err) {
    console.error("Search error:", err);
    showGeoNotification("Error performing location search.", true);
  } finally {
    setGeoLoading(false);
  }
}

function getGeoUserLocation() {
  if (!navigator.geolocation) {
    showGeoNotification("Geolocation is not supported by your browser.", true);
    return;
  }

  setGeoLoading(true);
  navigator.geolocation.getCurrentPosition(
    async (position) => {
      setGeoLoading(false);
      geoUserLocation = {
        lat: position.coords.latitude,
        lng: position.coords.longitude,
      };

      updateGeoUserMarker();

      if (geoMapInstance) {
        geoMapInstance.flyTo([geoUserLocation.lat, geoUserLocation.lng], 14);
      }

      await loadGeoPins(geoUserLocation.lat, geoUserLocation.lng);
      showGeoNotification("Located your position!");
    },
    (error) => {
      setGeoLoading(false);
      let msg = "Unable to retrieve position.";
      if (error.code === 1) msg = "Location permission denied.";
      else if (error.code === 2) msg = "Location position unavailable.";
      else if (error.code === 3) msg = "Location request timed out.";
      showGeoNotification(msg, true);
    },
    { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
  );
}

function updateGeoUserMarker() {
  if (!geoUserLocation || !geoMapInstance) return;

  if (geoUserMarker) {
    geoMapInstance.removeLayer(geoUserMarker);
  }

  const userIcon = L.divIcon({
    html: `<div style="background-color: #10B981; width: 22px; height: 22px; border-radius: 50%; border: 3px solid #FFFFFF; box-shadow: 0 0 12px rgba(16,185,129,0.9);"></div>`,
    className: "",
    iconSize: [22, 22],
    iconAnchor: [11, 11],
  });

  geoUserMarker = L.marker([geoUserLocation.lat, geoUserLocation.lng], { icon: userIcon })
    .addTo(geoMapInstance)
    .bindPopup("<b>Your Current Position</b>");
}

function showGeoNotification(msg, isError = false) {
  const notifEl = document.getElementById("notification-message");
  if (!notifEl) return;
  notifEl.textContent = msg;
  notifEl.style.backgroundColor = isError ? "rgba(220, 38, 38, 0.95)" : "rgba(79, 70, 229, 0.95)";
  notifEl.classList.remove("hidden");
  setTimeout(() => notifEl.classList.add("hidden"), 4000);
}

function setGeoLoading(isLoading) {
  const overlay = document.getElementById("loading-overlay");
  if (!overlay) return;
  if (isLoading) overlay.classList.remove("hidden");
  else overlay.classList.add("hidden");
}
