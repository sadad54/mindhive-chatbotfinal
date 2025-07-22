import sqlite3
import os
import re
from typing import List, Dict, Any, Optional
from app.models.schemas import ToolResult, OutletResult

class OutletDatabase:
    """SQLite database for ZUS Coffee outlets"""
    
    def __init__(self, db_path: str = "./data/outlets.db"):
        self.db_path = db_path
        self._ensure_database()
    
    def _ensure_database(self):
        """Ensure database exists and is populated"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            # Create outlets table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS outlets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    location TEXT NOT NULL,
                    address TEXT NOT NULL,
                    opening_hours TEXT NOT NULL,
                    services TEXT,  -- JSON string of services
                    contact TEXT,
                    latitude REAL,
                    longitude REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Check if data exists
            cursor = conn.execute("SELECT COUNT(*) FROM outlets")
            count = cursor.fetchone()[0]
            
            if count == 0:
                self._populate_sample_data(conn)
    
    def _populate_sample_data(self, conn):
        """Populate database with sample ZUS Coffee outlet data"""
        outlets_data = [
            {
                "name": "ZUS Coffee SS2",
                "location": "SS2, Petaling Jaya",
                "address": "G-01, Jalan SS 2/61, SS 2, 47300 Petaling Jaya, Selangor",
                "opening_hours": "7:00 AM - 10:00 PM",
                "services": '["Dine-in", "Takeaway", "Delivery", "WiFi", "Power outlets"]',
                "contact": "+603-7875-1234",
                "latitude": 3.1127,
                "longitude": 101.6324
            },
            {
                "name": "ZUS Coffee Bangsar",
                "location": "Bangsar, Kuala Lumpur",
                "address": "G-12, Jalan Telawi 2, Bangsar Baru, 59100 Kuala Lumpur",
                "opening_hours": "6:30 AM - 11:00 PM",
                "services": '["Dine-in", "Takeaway", "Drive-thru", "WiFi", "Meeting rooms"]',
                "contact": "+603-2284-5678",
                "latitude": 3.1204,
                "longitude": 101.6769
            },
            {
                "name": "ZUS Coffee KLCC",
                "location": "KLCC, Kuala Lumpur",
                "address": "Level 2, Suria KLCC, 50088 Kuala Lumpur",
                "opening_hours": "10:00 AM - 10:00 PM",
                "services": '["Dine-in", "Takeaway", "WiFi"]',
                "contact": "+603-2382-9012",
                "latitude": 3.1578,
                "longitude": 101.7118
            },
            {
                "name": "ZUS Coffee Mont Kiara",
                "location": "Mont Kiara, Kuala Lumpur",
                "address": "G-01, Plaza Mont Kiara, 50480 Kuala Lumpur",
                "opening_hours": "7:00 AM - 9:00 PM",
                "services": '["Dine-in", "Takeaway", "WiFi", "Power outlets", "Outdoor seating"]',
                "contact": "+603-6201-3456",
                "latitude": 3.1721,
                "longitude": 101.6505
            },
            {
                "name": "ZUS Coffee Sunway Pyramid",
                "location": "Sunway, Selangor",
                "address": "LG2-23A, Sunway Pyramid, 47500 Subang Jaya, Selangor",
                "opening_hours": "10:00 AM - 10:00 PM",
                "services": '["Dine-in", "Takeaway", "WiFi"]',
                "contact": "+603-7492-7890",
                "latitude": 3.0733,
                "longitude": 101.6068
            },
            {
                "name": "ZUS Coffee Damansara Heights",
                "location": "Damansara Heights, Kuala Lumpur",
                "address": "G-05, Jalan Semantan, Damansara Heights, 50490 Kuala Lumpur",
                "opening_hours": "6:30 AM - 10:30 PM",
                "services": '["Dine-in", "Takeaway", "Drive-thru", "WiFi", "Power outlets"]',
                "contact": "+603-2093-4567",
                "latitude": 3.1496,
                "longitude": 101.6618
            }
        ]
        
        for outlet in outlets_data:
            conn.execute('''
                INSERT INTO outlets (name, location, address, opening_hours, services, contact, latitude, longitude)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                outlet["name"], outlet["location"], outlet["address"],
                outlet["opening_hours"], outlet["services"], outlet["contact"],
                outlet["latitude"], outlet["longitude"]
            ))
        
        conn.commit()
        print("Sample outlet data populated.")
    
    def execute_query(self, sql_query: str) -> List[Dict[str, Any]]:
        """Execute SQL query and return results"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row  # Return dict-like rows
            cursor = conn.execute(sql_query)
            return [dict(row) for row in cursor.fetchall()]

class Text2SQLConverter:
    """Converts natural language queries to SQL for outlet database"""
    
    def __init__(self):
        self.schema = {
            "outlets": {
                "columns": [
                    "id", "name", "location", "address", "opening_hours",
                    "services", "contact", "latitude", "longitude"
                ],
                "description": "Table containing ZUS Coffee outlet information"
            }
        }
    
    def convert(self, natural_query: str) -> str:
        """Convert natural language to SQL query"""
        query_lower = natural_query.lower().strip()
        
        # Basic query patterns
        if self._is_location_query(query_lower):
            return self._build_location_query(query_lower)
        elif self._is_hours_query(query_lower):
            return self._build_hours_query(query_lower)
        elif self._is_services_query(query_lower):
            return self._build_services_query(query_lower)
        elif self._is_contact_query(query_lower):
            return self._build_contact_query(query_lower)
        else:
            # Default: search by location or name
            return self._build_general_search_query(query_lower)
    
    def _is_location_query(self, query: str) -> bool:
        """Check if query is asking about location"""
        location_keywords = ["outlet", "store", "branch", "location", "where", "in", "at"]
        return any(keyword in query for keyword in location_keywords)
    
    def _is_hours_query(self, query: str) -> bool:
        """Check if query is asking about opening hours"""
        hours_keywords = ["hour", "time", "open", "close", "when"]
        return any(keyword in query for keyword in hours_keywords)
    
    def _is_services_query(self, query: str) -> bool:
        """Check if query is asking about services"""
        service_keywords = ["service", "wifi", "delivery", "drive", "takeaway", "dine"]
        return any(keyword in query for keyword in service_keywords)
    
    def _is_contact_query(self, query: str) -> bool:
        """Check if query is asking about contact info"""
        contact_keywords = ["contact", "phone", "number", "call"]
        return any(keyword in query for keyword in contact_keywords)
    
    def _extract_location(self, query: str) -> Optional[str]:
        """Extract location from query"""
        # Common location patterns
        locations = [
            "ss2", "ss 2", "bangsar", "klcc", "mont kiara", "sunway", "damansara",
            "petaling jaya", "kuala lumpur", "selangor", "pj", "kl"
        ]
        
        for location in locations:
            if location in query:
                return location
        
        # Try to extract location after "in" or "at"
        location_match = re.search(r"(?:in|at)\s+([a-zA-Z\s]+?)(?:\s|$|[?.,])", query)
        if location_match:
            return location_match.group(1).strip()
        
        return None
    
    def _build_location_query(self, query: str) -> str:
        """Build SQL query for location searches"""
        location = self._extract_location(query)
        
        if location:
            # Normalize location for better matching
            location_clean = location.replace(" ", "").lower()
            
            # Special handling for common abbreviations
            if location_clean == "pj":
                location = "petaling jaya"
            elif location_clean == "kl":
                location = "kuala lumpur"
            elif location_clean in ["ss2", "ss 2"]:
                location = "SS2"
            
            return f"""
                SELECT * FROM outlets 
                WHERE LOWER(location) LIKE '%{location.lower()}%' 
                   OR LOWER(address) LIKE '%{location.lower()}%'
                   OR LOWER(name) LIKE '%{location.lower()}%'
                ORDER BY name
            """
        else:
            return "SELECT * FROM outlets ORDER BY name"
    
    def _build_hours_query(self, query: str) -> str:
        """Build SQL query for hours information"""
        location = self._extract_location(query)
        
        if location:
            location_clean = location.replace(" ", "").lower()
            if location_clean == "pj":
                location = "petaling jaya"
            elif location_clean == "kl":
                location = "kuala lumpur"
            elif location_clean in ["ss2", "ss 2"]:
                location = "SS2"
            
            return f"""
                SELECT name, location, opening_hours FROM outlets 
                WHERE LOWER(location) LIKE '%{location.lower()}%' 
                   OR LOWER(address) LIKE '%{location.lower()}%'
                   OR LOWER(name) LIKE '%{location.lower()}%'
                ORDER BY name
            """
        else:
            return "SELECT name, location, opening_hours FROM outlets ORDER BY name"
    
    def _build_services_query(self, query: str) -> str:
        """Build SQL query for services information"""
        location = self._extract_location(query)
        
        base_query = "SELECT name, location, services FROM outlets"
        
        if location:
            base_query += f" WHERE LOWER(location) LIKE '%{location.lower()}%' OR LOWER(address) LIKE '%{location.lower()}%'"
        
        # Check for specific services
        if "wifi" in query:
            base_query += " AND LOWER(services) LIKE '%wifi%'" if "WHERE" in base_query else " WHERE LOWER(services) LIKE '%wifi%'"
        elif "delivery" in query:
            base_query += " AND LOWER(services) LIKE '%delivery%'" if "WHERE" in base_query else " WHERE LOWER(services) LIKE '%delivery%'"
        elif "drive" in query:
            base_query += " AND LOWER(services) LIKE '%drive%'" if "WHERE" in base_query else " WHERE LOWER(services) LIKE '%drive%'"
        
        return base_query + " ORDER BY name"
    
    def _build_contact_query(self, query: str) -> str:
        """Build SQL query for contact information"""
        location = self._extract_location(query)
        
        if location:
            return f"""
                SELECT name, location, contact FROM outlets 
                WHERE LOWER(location) LIKE '%{location.lower()}%' 
                   OR LOWER(address) LIKE '%{location.lower()}%'
                   OR LOWER(name) LIKE '%{location.lower()}%'
                ORDER BY name
            """
        else:
            return "SELECT name, location, contact FROM outlets ORDER BY name"
    
    def _build_general_search_query(self, query: str) -> str:
        """Build general search query"""
        # Extract any meaningful keywords
        search_terms = []
        words = query.split()
        
        # Filter out common stop words
        stop_words = {"is", "there", "a", "an", "the", "in", "at", "on", "what", "where", "how", "can", "do"}
        meaningful_words = [word for word in words if word.lower() not in stop_words and len(word) > 2]
        
        if meaningful_words:
            search_term = " ".join(meaningful_words)
            return f"""
                SELECT * FROM outlets 
                WHERE LOWER(name) LIKE '%{search_term.lower()}%' 
                   OR LOWER(location) LIKE '%{search_term.lower()}%'
                   OR LOWER(address) LIKE '%{search_term.lower()}%'
                ORDER BY name
            """
        else:
            return "SELECT * FROM outlets ORDER BY name LIMIT 5"

class OutletsTool:
    """Tool for outlet information using Text2SQL"""
    
    def __init__(self, db_path: str = "./data/outlets.db"):
        self.database = OutletDatabase(db_path)
        self.text2sql = Text2SQLConverter()
    
    async def execute(self, query: str) -> ToolResult:
        """Execute outlet query using Text2SQL"""
        try:
            # Convert natural language to SQL
            sql_query = self.text2sql.convert(query)
            
            # Validate SQL query for safety
            if not self._is_safe_query(sql_query):
                return ToolResult(
                    success=False,
                    error_message="Query not allowed for security reasons",
                    tool_name="outlets"
                )
            
            # Execute SQL query
            raw_results = self.database.execute_query(sql_query)
            
            # Convert to OutletResult format
            outlet_results = []
            for row in raw_results:
                # Parse services JSON
                services = []
                if row.get("services"):
                    try:
                        import json
                        services = json.loads(row["services"])
                    except:
                        services = []
                
                outlet_result = OutletResult(
                    id=row["id"],
                    name=row["name"],
                    location=row["location"],
                    address=row["address"],
                    opening_hours=row["opening_hours"],
                    services=services,
                    contact=row.get("contact")
                )
                outlet_results.append(outlet_result)
            
            return ToolResult(
                success=True,
                data={
                    "query": query,
                    "sql_query": sql_query.strip(),
                    "results": [result.dict() for result in outlet_results],
                    "total_found": len(outlet_results)
                },
                tool_name="outlets"
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error_message=f"Outlet query error: {str(e)}",
                tool_name="outlets"
            )
    
    def _is_safe_query(self, sql_query: str) -> bool:
        """Check if SQL query is safe to execute"""
        sql_lower = sql_query.lower().strip()
        
        # Only allow SELECT statements
        if not sql_lower.startswith("select"):
            return False
        
        # Disallow dangerous keywords
        dangerous_keywords = [
            "drop", "delete", "insert", "update", "alter", "create",
            "truncate", "exec", "execute", "union", "--", "/*", "*/"
        ]
        
        for keyword in dangerous_keywords:
            if keyword in sql_lower:
                return False
        
        return True
    
    def add_outlet(self, outlet_data: Dict[str, Any]):
        """Add a new outlet to the database"""
        with sqlite3.connect(self.database.db_path) as conn:
            conn.execute('''
                INSERT INTO outlets (name, location, address, opening_hours, services, contact, latitude, longitude)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                outlet_data["name"], outlet_data["location"], outlet_data["address"],
                outlet_data["opening_hours"], outlet_data.get("services", "[]"),
                outlet_data.get("contact"), outlet_data.get("latitude"), outlet_data.get("longitude")
            ))
            conn.commit()
    
    def get_all_outlets(self) -> List[Dict[str, Any]]:
        """Get all outlets"""
        return self.database.execute_query("SELECT * FROM outlets ORDER BY name")
