# Travelling-Salesman-Problem-For-Multi-Agent-RAG-AI
Travelling Salesman Problem Using ACOA, Amoeba TSP and Graph Traversal Algorithms

## Data Understanding
# Data Dictionary: Sub-Saharan Transport Dataset

This dataset contains 1000 records of vehicle travel data across different cities in Sub-Saharan Africa. It includes information on city pairs, vehicle characteristics, traffic congestion, and travel-related metrics.

## Columns and Descriptions

### **1. City of Origin** (`string`)
   - The starting city of the trip.
   - Example: `"Kigali"`

### **2. Destination City** (`string`)
   - The final city where the vehicle is traveling.
   - Example: `"Butare"`

### **3. Stopover City** (`string, nullable`)
   - An intermediate city where the vehicle may make a stop before reaching the final destination.
   - If no stopover exists, the value is `null`.
   - Example: `"Arusha"` or `null`

### **4. Vehicle Plate** (`string, unique identifier`)
   - A unique identifier for each vehicle in the format: `"XXX-XXX-####"`
   - The first three characters represent the first three letters of the origin city, the next three represent the destination city, followed by a four-digit serial number.
   - Example: `"KIG-BUT-0001"`

### **5. Vehicle Type** (`categorical`)
   - The type of vehicle used for the trip.
   - Possible values:
     - `"SUV"`
     - `"Truck"`
     - `"Saloon"`
     - `"Coupe"`
     - `"Hybrid"`
   - Example: `"Truck"`

### **6. Speed (km/h)** (`float`)
   - The average speed of the vehicle during travel.
   - Speed varies depending on the vehicle type.
   - Example: `85.4`

### **7. Load Weight (tons)** (`float`)
   - The weight of the cargo or passengers carried by the vehicle.
   - Example: `3.2`

### **8. Fuel Consumption (L/100km)** (`float`)
   - The amount of fuel consumed by the vehicle per 100 km.
   - Example: `12.5`

### **9. Traffic Congestion** (`categorical`)
   - The level of traffic congestion during the trip.
   - Possible values:
     - `"Low"`
     - `"Medium"`
     - `"High"`
   - Example: `"High"`

### **10. Driving Distance (km)** (`float`)
   - The precomputed driving distance between the origin and destination city.
   - Derived from Google Maps data.
   - Example: `125.0`

### **11. Travel Time (hours)** (`float`)
   - The estimated time taken to travel based on speed and driving distance.
   - Calculated as:  
     \[
     \text{Travel Time} = \frac{\text{Driving Distance}}{\text{Speed}}
     \]
   - Example: `2.5`

### **12. Adjusted Travel Time (hours)** (`float`)
   - The estimated travel time after accounting for traffic congestion.
   - Speed is adjusted by ±20 km/h based on traffic:
     - `"Low"` congestion: Speed increases by 20 km/h.
     - `"High"` congestion: Speed decreases by 20 km/h.
     - `"Medium"` congestion: No change.
   - Example: `2.8`

### **13. Peak Time Indicator** (`boolean`)
   - Indicates whether the travel occurs during peak hours.
   - Peak hours are derived from the adjusted travel time.
   - `True` if the trip overlaps with typical peak hours, otherwise `False`.
   - Example: `True`

### **14. Off-Peak Time Indicator** (`boolean`)
   - Indicates whether the travel occurs during off-peak hours.
   - Off-peak hours are derived from the adjusted travel time.
   - Example: `False`

### **15. Travel Time Index** (`float`)
   - A measure of traffic efficiency calculated as:
     \[
     \text{Travel Time Index} = \frac{\text{Adjusted Travel Time}}{\text{Travel Time}}
     \]
   - A value greater than `1.0` indicates congestion delays.
   - Example: `1.12`


 
