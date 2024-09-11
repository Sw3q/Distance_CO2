from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Define emission factors (in kg CO2 per liter)
emission_factors = {
    'diesel': 2.68,
    'gasoline': 2.31,
    'electric': 0  # Assuming 0 CO2 if fully electric, or you can use local grid emission data
}

def get_distance(origin, destination, api_key):
    """
    Get the distance between two locations using the Google Distance Matrix API.
    """
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    
    # Define the parameters for the API request
    params = {
        'origins': origin,
        'destinations': destination,
        'key': api_key,
        'mode': 'driving'  # You can change this to 'walking', 'bicycling', or 'transit' if needed
    }
    
    # Make the API request
    response = requests.get(url, params=params)
    
    # Parse the JSON response
    data = response.json()
    
    try:
        # Extract the distance in kilometers (Google API returns distance in meters)
        distance = data['rows'][0]['elements'][0]['distance']['value'] / 1000  # Convert meters to kilometers
        return distance
    except (KeyError, IndexError):
        return None

def calculate_co2(distance, fuel_efficiency, fuel_type):
    """
    Calculate the CO2 emissions for a trip given the distance, fuel efficiency, and fuel type.
    """
    # Check if the fuel type is valid
    if fuel_type not in emission_factors:
        return "Invalid fuel type"
    
    # Get the emission factor for the given fuel type
    emission_factor = emission_factors[fuel_type]
    
    # Calculate CO2 emissions
    co2_emissions = (distance * fuel_efficiency / 100) * emission_factor
    return co2_emissions

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        origin = request.form["origin"]
        destination = request.form["destination"]
        fuel_efficiency = float(request.form["fuel_efficiency"])
        fuel_type = request.form["fuel_type"].lower()
        api_key = 'AIzaSyAMTdWzxutENaSYB9CGsWRPNRRN6Ql0yPY'  # Replace with your Google Maps API key
        
        # Get the distance using Google Maps API
        distance = get_distance(origin, destination, api_key)
        
        if distance is None:
            result = "Error: Pas trouvé (Distances sont dans le même continent?) (Check API)"
        else:
            co2_emissions = calculate_co2(distance, fuel_efficiency, fuel_type)
            if isinstance(co2_emissions, str):
                result = co2_emissions
            else:
                result = f"The distance between {origin} and {destination} is approximately {distance:.2f} kilometers. CO2 emissions for the trip: {co2_emissions:.2f} kg"
        
        return render_template("index.html", result=result)
    return render_template("index.html", result="")

if __name__ == "__main__":
    app.run(debug=True)
