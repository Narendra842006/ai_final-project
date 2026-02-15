"""
Hospital Finder Service using Google Maps API
Includes live occupancy simulation and wait time estimation
"""
import os
import random
from typing import List, Tuple
from datetime import datetime
import googlemaps
from dotenv import load_dotenv
from .models import HospitalInfo
from .priority_queue import global_queue

load_dotenv()


class HospitalFinderService:
    """
    Service to find nearby hospitals using Google Maps API
    Simulates live occupancy and wait times
    """
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        self.gmaps = None
        
        if self.api_key and self.api_key != "your_google_maps_api_key_here":
            try:
                self.gmaps = googlemaps.Client(key=self.api_key)
                print("✅ Google Maps API initialized")
            except Exception as e:
                print(f"⚠️ Google Maps API error: {e}")
                print("📝 Using fallback hospital data")
        else:
            print("⚠️ Google Maps API key not found in environment")
            print("📝 Using fallback hospital data")
    
    def get_nearby_hospitals(
        self, 
        latitude: float, 
        longitude: float, 
        radius_km: float = 10.0,
        limit: int = 5
    ) -> List[HospitalInfo]:
        """
        Find nearby hospitals within radius
        
        Args:
            latitude: User's latitude
            longitude: User's longitude
            radius_km: Search radius in kilometers
            limit: Maximum number of results
        
        Returns:
            List of HospitalInfo objects with live occupancy and wait times
        """
        if self.gmaps:
            try:
                # Search for hospitals using Places API
                places_result = self.gmaps.places_nearby(
                    location=(latitude, longitude),
                    radius=radius_km * 1000,  # Convert km to meters
                    type='hospital',
                    keyword='emergency'
                )
                
                hospitals = []
                for place in places_result.get('results', [])[:limit]:
                    hospital_info = self._parse_google_place(place, latitude, longitude)
                    hospitals.append(hospital_info)
                
                return hospitals
            
            except Exception as e:
                print(f"⚠️ Google Maps API error: {e}")
                return self._get_fallback_hospitals(latitude, longitude, limit)
        else:
            return self._get_fallback_hospitals(latitude, longitude, limit)
    
    def _parse_google_place(
        self, 
        place: dict, 
        user_lat: float, 
        user_lng: float
    ) -> HospitalInfo:
        """Parse Google Places API result into HospitalInfo"""
        # Extract data
        name = place.get('name', 'Unknown Hospital')
        address = place.get('vicinity', 'Address not available')
        place_lat = place['geometry']['location']['lat']
        place_lng = place['geometry']['location']['lng']
        rating = place.get('rating')
        
        # Calculate distance
        distance_km = self._calculate_distance(user_lat, user_lng, place_lat, place_lng)
        
        # Estimate travel time (assume 40 km/h average urban speed)
        travel_time_minutes = int((distance_km / 40) * 60) + 5  # +5 min buffer
        
        # Simulate live occupancy and wait time
        live_occupancy, wait_time = self._simulate_hospital_status()
        
        # Determine facilities (simplified - in production, use Place Details API)
        has_emergency = 'emergency' in name.lower() or 'hospital' in name.lower()
        has_icu = random.choice([True, False])  # In production, use actual data
        
        return HospitalInfo(
            name=name,
            address=address,
            distance_km=round(distance_km, 2),
            travel_time_minutes=travel_time_minutes,
            live_occupancy=live_occupancy,
            estimated_wait_time=wait_time,
            has_emergency=has_emergency,
            has_icu=has_icu,
            rating=rating
        )
    
    def _calculate_distance(
        self, 
        lat1: float, 
        lon1: float, 
        lat2:float, 
        lon2: float
    ) -> float:
        """Calculate distance between two coordinates using Haversine formula"""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Earth's radius in km
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = R * c
        
        return distance
    
    def _simulate_hospital_status(self) -> Tuple[float, int]:
        """
        Simulate live occupancy and wait time
        
        In production, this would connect to real hospital data systems
        For now, we simulate based on current queue status and time of day
        """
        # Get current queue statistics
        queue_size = global_queue.get_queue_size()
        immediate_count = global_queue.get_immediate_count()
        
        # Base occupancy (50-85%)
        base_occupancy = random.uniform(50, 85)
        
        # Adjust based on current hour (simulate rush hours)
        current_hour = datetime.now().hour
        if 8 <= current_hour <= 12:  # Morning rush
            base_occupancy += random.uniform(5, 15)
        elif 18 <= current_hour <= 22:  # Evening rush
            base_occupancy += random.uniform(10, 20)
        
        # Adjust based on our queue (if many patients, hospitals likely busy too)
        occupancy_boost = min(queue_size * 2, 15)
        live_occupancy = min(base_occupancy + occupancy_boost, 100)
        
        # Calculate wait time based on occupancy
        # Formula: Base wait (15 min) + occupancy factor + immediate patient penalty
        base_wait = 15
        occupancy_wait = int((live_occupancy / 100) * 60)  # Up to 60 min from occupancy
        immediate_penalty = immediate_count * 10  # Each critical patient adds 10 min
        
        estimated_wait = base_wait + occupancy_wait + immediate_penalty
        estimated_wait = min(estimated_wait, 240)  # Cap at 4 hours
        
        return round(live_occupancy, 1), estimated_wait
    
    def _get_fallback_hospitals(
        self, 
        latitude: float, 
        longitude: float, 
        limit: int
    ) -> List[HospitalInfo]:
        """
        Fallback hospital data when Google Maps API is unavailable
        Returns simulated nearby hospitals
        """
        fallback_hospitals = [
            {
                "name": "City General Hospital",
                "address": "123 Main Street, Downtown",
                "distance_km": 2.5,
                "has_emergency": True,
                "has_icu": True,
                "rating": 4.2
            },
            {
                "name": "Regional Medical Center",
                "address": "456 Oak Avenue, Midtown",
                "distance_km": 4.8,
                "has_emergency": True,
                "has_icu": True,
                "rating": 4.5
            },
            {
                "name": "Community Health Clinic",
                "address": "789 Pine Road, Suburbs",
                "distance_km": 6.2,
                "has_emergency": False,
                "has_icu": False,
                "rating": 3.8
            },
            {
                "name": "St. Mary's Hospital",
                "address": "321 Elm Street, Eastside",
                "distance_km": 7.1,
                "has_emergency": True,
                "has_icu": True,
                "rating": 4.7
            },
            {
                "name": "University Medical Hospital",
                "address": "654 University Drive, Campus",
                "distance_km": 9.3,
                "has_emergency": True,
                "has_icu": True,
                "rating": 4.6
            }
        ]
        
        results = []
        for hospital in fallback_hospitals[:limit]:
            occupancy, wait_time = self._simulate_hospital_status()
            travel_time = int((hospital['distance_km'] / 40) * 60) + 5
            
            results.append(HospitalInfo(
                name=hospital['name'],
                address=hospital['address'],
                distance_km=hospital['distance_km'],
                travel_time_minutes=travel_time,
                live_occupancy=occupancy,
                estimated_wait_time=wait_time,
                has_emergency=hospital['has_emergency'],
                has_icu=hospital['has_icu'],
                rating=hospital['rating']
            ))
        
        return results


# Global hospital service instance
hospital_service = HospitalFinderService()
