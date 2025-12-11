document.addEventListener('DOMContentLoaded', () => {
    const getWeatherBtn = document.getElementById('get-weather');
    const locationInput = document.getElementById('location');
    const startDateInput = document.getElementById('start-date');
    const endDateInput = document.getElementById('end-date');
    const errorMessage = document.getElementById('error-message');
    const weatherDisplay = document.getElementById('weather-display');
    const locationTitle = document.getElementById('location-title');
    const weatherIcon = document.getElementById('weather-icon');
    const temperature = document.getElementById('temperature');
    const description = document.getElementById('description');
    const dateRange = document.getElementById('date-range');

    getWeatherBtn.addEventListener('click', async () => {
        const location = locationInput.value.trim();
        const startDate = startDateInput.value;
        const endDate = endDateInput.value;

        if (!location) {
            showError('Please enter a location.');
            return;
        }

        const body = { location };
        const isForecast = startDate && endDate;
        if (isForecast) {
            if (new Date(startDate) > new Date(endDate)) {
                showError('Start date must be before end date.');
                return;
            }
            body.date_range_start = startDate;
            body.date_range_end = endDate;
        }

        try {
            const response = await fetch('http://127.0.0.1:8000/weather/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });

            if (!response.ok) {
                const errorData = await response.json();
                showError(errorData.detail || 'Failed to fetch weather.');
                return;
            }

            const data = await response.json();
            showWeather(data, isForecast);
        } catch (err) {
            showError('Network error: ' + err.message);
        }
    });

    function showError(msg) {
        errorMessage.textContent = msg;
        errorMessage.classList.remove('hidden');
        weatherDisplay.classList.add('hidden');
    }

    function showWeather(data, isForecast) {
        errorMessage.classList.add('hidden');
        weatherDisplay.classList.remove('hidden');

        locationTitle.textContent = `${data.location} ${isForecast ? 'Forecast' : 'Current Weather'}`;
        temperature.textContent = `Temperature: ${data.temperature} °C`;
        description.textContent = `Description: ${data.weather_description}`;
        dateRange.textContent = isForecast ? `From ${data.date_range_start} to ${data.date_range_end}` : '';

        // Map description to icon code (simplified; adjust as needed)
        const iconMap = {
            'clear sky': '01d',
            'few clouds': '02d',
            'scattered clouds': '03d',
            'broken clouds': '04d',
            'shower rain': '09d',
            'rain': '10d',
            'thunderstorm': '11d',
            'snow': '13d',
            'mist': '50d',
            // Add more mappings based on OpenWeather descriptions
            'Forecast average': '04d'  // Default for aggregate
        };
        const iconCode = iconMap[data.weather_description.toLowerCase()] || '01d';
        weatherIcon.src = `https://openweathermap.org/img/wn/${iconCode}@2x.png`;
    }
});