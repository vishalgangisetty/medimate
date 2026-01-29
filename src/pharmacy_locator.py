from typing import List, Dict, Optional
import requests
from src.config import Config
from src.utils import setup_logger

logger = setup_logger(__name__)


class PharmacyLocator:
    def __init__(self):
        self.api_key = Config.GOOGLE_API_KEY
        # Using new Places API endpoints
        self.places_url = "https://places.googleapis.com/v1/places"
        self.geocoding_url = "https://maps.googleapis.com/maps/api/geocode/json"
    
    def geocode_address(self, address: str) -> Optional[tuple]:
        """
        Geocode an address to coordinates
        Returns: (latitude, longitude) tuple or None if failed
        """
        if not self.api_key:
            logger.error("Google API Key not configured")
            return None
        try:
            params = {
                "address": address,
                "key": self.api_key
            }
            response = requests.get(self.geocoding_url, params=params, timeout=5)
            data = response.json()
            
            if data['status'] == 'OK' and data['results']:
                location = data['results'][0]['geometry']['location']
                formatted_addr = data['results'][0]['formatted_address']
                logger.info(f"Successfully geocoded: {formatted_addr}")
                return (location['lat'], location['lng'])
            elif data['status'] == 'REQUEST_DENIED':
                logger.warning("Geocoding API not enabled. Using default Chennai coordinates.")
                # Return Chennai coordinates as fallback
                return (13.0827, 80.2707)
            else:
                logger.warning(f"Geocoding failed: {data.get('status')} - {data.get('error_message', 'No message')}")
                return None
        except Exception as e:
            logger.error(f"Geocoding error: {str(e)}. Using default coordinates.")
            return (13.0827, 80.2707)
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance in meters using Haversine formula"""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371000  # Earth radius in meters
        
        phi1 = radians(lat1)
        phi2 = radians(lat2)
        delta_phi = radians(lat2 - lat1)
        delta_lambda = radians(lon2 - lon1)
        
        a = sin(delta_phi/2)**2 + cos(phi1) * cos(phi2) * sin(delta_lambda/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    def find_nearby_pharmacies(
        self,
        latitude: float,
        longitude: float,
        radius: int = 5000,
        max_results: int = 10
    ) -> List[Dict]:
        if not self.api_key:
            logger.warning("Google API Key not configured. Using sample data.")
            return self._get_sample_pharmacies_with_distance(latitude, longitude, radius)
        try:
            search_url = f"{self.places_url}/nearbysearch/json"
            params = {
                "location": f"{latitude},{longitude}",
                "radius": radius,
                "type": "pharmacy",
                "key": self.api_key
            }
            
            response = requests.get(search_url, params=params, timeout=5)
            data = response.json()
            
            if data['status'] != 'OK':
                error_msg = data.get('error_message', 'Unknown error')
                logger.warning(f"Places API returned status: {data['status']} - {error_msg}")
                if data['status'] == 'REQUEST_DENIED':
                    logger.error("API not enabled. Using sample data instead.")
                return self._get_sample_pharmacies_with_distance(latitude, longitude, radius)
            
            pharmacies = []
            for place in data.get('results', [])[:max_results]:
                place_id = place['place_id']
                place_lat = place['geometry']['location']['lat']
                place_lon = place['geometry']['location']['lng']
                
                # Calculate actual distance
                distance = self._calculate_distance(latitude, longitude, place_lat, place_lon)
                
                # Get detailed information including phone number
                details = self._get_place_details(place_id)
                
                pharmacy_info = {
                    "name": place.get('name', 'Unknown'),
                    "address": place.get('vicinity', 'Address not available'),
                    "latitude": place_lat,
                    "longitude": place_lon,
                    "distance": distance,  # in meters
                    "rating": place.get('rating', 0),
                    "total_ratings": place.get('user_ratings_total', 0),
                    "is_open_now": place.get('opening_hours', {}).get('open_now', False),
                    "place_id": place_id
                }
                
                # Add details from place details API
                if details:
                    pharmacy_info.update(details)
                
                pharmacies.append(pharmacy_info)
            
            # Sort by distance
            pharmacies.sort(key=lambda x: x.get('distance', float('inf')))
            
            logger.info(f"Found {len(pharmacies)} pharmacies")
            return pharmacies
        
        except Exception as e:
            logger.error(f"Error finding pharmacies: {str(e)}. Using sample data.")
            return self._get_sample_pharmacies_with_distance(latitude, longitude, radius)
    
    def _get_place_details(self, place_id: str) -> Optional[Dict]:
        """Get detailed information for a place including phone number"""
        try:
            details_url = f"{self.places_url}/details/json"
            params = {
                "place_id": place_id,
                "fields": "formatted_phone_number,international_phone_number,website,opening_hours",
                "key": self.api_key
            }
            
            response = requests.get(details_url, params=params)
            data = response.json()
            
            if data['status'] != 'OK':
                return None
            
            result = data.get('result', {})
            
            return {
                "phone": result.get('formatted_phone_number') or result.get('international_phone_number'),
                "website": result.get('website'),
                "hours": result.get('opening_hours', {}).get('weekday_text', [])
            }
        
        except Exception as e:
            logger.error(f"Error getting place details: {str(e)}")
            return None
    
    def search_pharmacy_by_name(
        self,
        pharmacy_name: str,
        latitude: float,
        longitude: float,
        radius: int = 10000
    ) -> List[Dict]:
        """Search for a specific pharmacy by name"""
        try:
            search_url = f"{self.places_url}/nearbysearch/json"
            params = {
                "location": f"{latitude},{longitude}",
                "radius": radius,
                "type": "pharmacy",
                "keyword": pharmacy_name,
                "key": self.api_key
            }
            
            response = requests.get(search_url, params=params)
            data = response.json()
            
            if data['status'] != 'OK':
                return []
            
            results = []
            for place in data.get('results', []):
                details = self._get_place_details(place['place_id'])
                
                pharmacy_info = {
                    "name": place.get('name'),
                    "address": place.get('vicinity'),
                    "latitude": place['geometry']['location']['lat'],
                    "longitude": place['geometry']['location']['lng'],
                    "rating": place.get('rating', 0),
                    "place_id": place['place_id']
                }
                
                if details:
                    pharmacy_info.update(details)
                
                results.append(pharmacy_info)
            
            return results
        
        except Exception as e:
            logger.error(f"Error searching pharmacy: {str(e)}")
            return []
    
    def get_directions_url(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float
    ) -> str:
        """Generate Google Maps directions URL"""
        return f"https://www.google.com/maps/dir/?api=1&origin={origin_lat},{origin_lng}&destination={dest_lat},{dest_lng}&travelmode=driving"
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two coordinates in kilometers
        Using Haversine formula
        """
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Earth's radius in km
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    def _get_sample_pharmacies_with_distance(self, latitude: float, longitude: float, radius: int) -> List[Dict]:
        """Return sample pharmacies when API is not available"""
        import random
        
        # Generate pharmacies near the given location
        sample_pharmacies = []
        pharmacy_data = [
            {"name": "Apollo Pharmacy", "phone": "+91-9876543210"},
            {"name": "MedPlus", "phone": "+91-9876543211"},
            {"name": "Netmeds Store", "phone": "+91-9876543212"},
            {"name": "HealthPlus Pharmacy", "phone": "+91-9876543213"},
            {"name": "Wellness Forever", "phone": "+91-9876543214"},
            {"name": "Guardian Pharmacy", "phone": "+91-9876543215"},
            {"name": "1mg Store", "phone": "+91-9876543216"},
            {"name": "PharmEasy Store", "phone": "+91-9876543217"}
        ]
        
        for i, data in enumerate(pharmacy_data[:5]):
            # Add small random offset to location
            offset_lat = random.uniform(-0.01, 0.01)
            offset_lng = random.uniform(-0.01, 0.01)
            distance = random.uniform(500, min(radius, 5000))
            
            sample_pharmacies.append({
                "name": data["name"],
                "address": f"{random.randint(1, 999)} Main Street, Shop {random.randint(1, 50)}, Local Area - {random.randint(600001, 600999)}",
                "phone": data["phone"],
                "latitude": latitude + offset_lat,
                "longitude": longitude + offset_lng,
                "distance": distance,
                "rating": round(random.uniform(3.5, 5.0), 1),
                "total_ratings": random.randint(50, 500),
                "is_open_now": random.choice([True, True, False]),
                "place_id": f"sample_{i}"
            })
        
        # Sort by distance
        sample_pharmacies.sort(key=lambda x: x['distance'])
        logger.info(f"Using {len(sample_pharmacies)} sample pharmacies")
        return sample_pharmacies


# Sample pharmacy data for demo (if API fails or for testing)
SAMPLE_PHARMACIES = [
    {
        "name": "Apollo Pharmacy",
        "address": "123 Main Street, City Center",
        "phone": "+91-9876543210",
        "rating": 4.5,
        "open_now": True,
        "latitude": 0.0,
        "longitude": 0.0
    },
    {
        "name": "MedPlus",
        "address": "456 Park Road, Near Hospital",
        "phone": "+91-9876543211",
        "rating": 4.3,
        "open_now": True,
        "latitude": 0.0,
        "longitude": 0.0
    },
    {
        "name": "Netmeds Local Store",
        "address": "789 Market Street",
        "phone": "+91-9876543212",
        "rating": 4.0,
        "open_now": False,
        "latitude": 0.0,
        "longitude": 0.0
    }
]
