document.addEventListener("DOMContentLoaded", () => {
  const locationInput = document.getElementById("location-input");
  const styleInput = document.getElementById("style-input");
  const generateBtn = document.getElementById("generate-btn");
  const geolocateBtn = document.getElementById("geolocate-btn");
  const loading = document.getElementById("loading");
  const errorAlert = document.getElementById("error-alert");
  const metadataFooter = document.getElementById("metadata-footer");
  const metaTitle = document.getElementById("meta-title");
  const metaSummary = document.getElementById("meta-summary");

  let renderer = new WeatherArtRenderer("canvas-container");
  let userCoords = null;

  function showError(message) {
    errorAlert.textContent = message;
    errorAlert.classList.remove("d-none");
  }

  function clearError() {
    errorAlert.classList.add("d-none");
    errorAlert.textContent = "";
  }

  function setLoading(on) {
    if (on) {
      loading.classList.remove("d-none");
      generateBtn.disabled = true;
    } else {
      loading.classList.add("d-none");
      generateBtn.disabled = false;
    }
  }

  geolocateBtn.addEventListener("click", () => {
    if (!navigator.geolocation) {
      showError("Geolocation is not supported by your browser.");
      return;
    }
    geolocateBtn.disabled = true;
    navigator.geolocation.getCurrentPosition(
      (position) => {
        userCoords = {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        };
        locationInput.value = `${userCoords.latitude.toFixed(2)}, ${userCoords.longitude.toFixed(2)}`;
        geolocateBtn.disabled = false;
      },
      (err) => {
        showError("Could not get your location: " + err.message);
        geolocateBtn.disabled = false;
      }
    );
  });

  generateBtn.addEventListener("click", generate);
  locationInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") generate();
  });

  async function generate() {
    clearError();
    const location = locationInput.value.trim();
    const stylePrompt = styleInput.value.trim();

    if (!location && !userCoords) {
      showError("Please enter a city name or use geolocation.");
      return;
    }

    const body = { style_prompt: stylePrompt };

    if (userCoords) {
      body.location = location || "My Location";
      body.latitude = userCoords.latitude;
      body.longitude = userCoords.longitude;
    } else {
      body.location = location;
    }

    setLoading(true);
    metadataFooter.classList.add("d-none");

    try {
      const resp = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      const data = await resp.json();

      if (!resp.ok) {
        showError(data.error || "Generation failed.");
        return;
      }

      renderer.render(data);

      if (data.scene && data.scene.metadata) {
        metaTitle.textContent = data.scene.metadata.title || "";
        metaSummary.textContent = data.scene.metadata.weather_summary || "";
        metadataFooter.classList.remove("d-none");
      }
    } catch (err) {
      showError("Request failed: " + err.message);
    } finally {
      setLoading(false);
    }
  }
});