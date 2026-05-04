const cityForm = document.getElementById("cityForm");
const cityInput = document.getElementById("cityInput");
const locationBtn = document.getElementById("locationBtn");
const defaultBtn = document.getElementById("defaultBtn");
const resultCard = document.getElementById("result");
const statusLabel = document.getElementById("status");

const placeEl = document.getElementById("place");
const timeEl = document.getElementById("time");
const tempEl = document.getElementById("temp");
const windEl = document.getElementById("wind");
const coordsEl = document.getElementById("coords");

const setStatus = (text, isError = false) => {
  statusLabel.textContent = text;
  statusLabel.style.color = isError ? "#b42318" : "#3f5f66";
};

const showWeather = (label, data) => {
  placeEl.textContent = label;
  timeEl.textContent = data.time ? `Updated: ${data.time}` : "Updated: N/A";
  tempEl.textContent = data.temperature !== null && data.temperature !== undefined ? `${data.temperature} C` : "N/A";
  windEl.textContent = data.windspeed !== null && data.windspeed !== undefined ? `${data.windspeed} km/h` : "N/A";
  coordsEl.textContent = `${data.latitude}, ${data.longitude}`;

  resultCard.classList.remove("hidden");
};

const fetchJson = async (url) => {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Request failed (${response.status})`);
  }
  return response.json();
};

const loadCityWeather = async (city) => {
  const cleanCity = city.trim();
  if (!cleanCity) {
    setStatus("Please enter a city name.", true);
    return;
  }

  setStatus(`Fetching weather for ${cleanCity}...`);
  try {
    const data = await fetchJson(`/weather/city?name=${encodeURIComponent(cleanCity)}`);

    if (data.found === false) {
      setStatus(`City not found: ${cleanCity}`, true);
      resultCard.classList.add("hidden");
      return;
    }

    showWeather(data.city || cleanCity, data);
    setStatus("City weather loaded.");
  } catch (error) {
    setStatus(error.message || "Could not fetch city weather.", true);
  }
};

const loadLatLonWeather = async (lat, lon) => {
  setStatus("Fetching weather for your location...");
  try {
    const data = await fetchJson(`/weather?lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lon)}`);
    showWeather("Your Location", data);
    setStatus("Location weather loaded.");
  } catch (error) {
    setStatus(error.message || "Could not fetch location weather.", true);
  }
};

cityForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  await loadCityWeather(cityInput.value);
});

locationBtn.addEventListener("click", () => {
  if (!navigator.geolocation) {
    setStatus("Geolocation is not supported by your browser.", true);
    return;
  }

  setStatus("Getting your coordinates...");
  navigator.geolocation.getCurrentPosition(
    (position) => {
      loadLatLonWeather(position.coords.latitude, position.coords.longitude);
    },
    () => {
      setStatus("Location permission denied or unavailable.", true);
    },
    { timeout: 10000 }
  );
});

defaultBtn.addEventListener("click", async () => {
  cityInput.value = "Lahore";
  await loadCityWeather("Lahore");
});

window.addEventListener("load", async () => {
  await loadCityWeather("Lahore");
});
