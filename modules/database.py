import sqlite3
import json
import hashlib
import os
from typing import Dict, Any, Optional, List

class PortfolioDB:
    """Simple database handler for portfolio tracker with authentication"""
    
    def __init__(self, db_path="portfolio_app.db"):
        """Initialize the database connection and create tables if needed"""
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        
        # Connect to database
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        
        # Create tables if they don't exist
        self._create_tables()
    
    def _create_tables(self):
        """Create the necessary database tables if they don't exist"""
        cursor = self.conn.cursor()
        
        # Users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            email TEXT,
            full_name TEXT
        )
        ''')
        
        # Portfolios table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS portfolios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            portfolio_data TEXT NOT NULL,
            cash_balance REAL DEFAULT 0,
            start_date TEXT,
            FOREIGN KEY (username) REFERENCES users (username)
        )
        ''')
        
        self.conn.commit()
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
    
    # User Management Functions
    def add_user(self, username: str, password: str, email: str = "", full_name: str = "") -> bool:
        """Add a new user to the database"""
        try:
            # Hash the password
            password_hash = self._hash_password(password)
            
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password_hash, email, full_name) VALUES (?, ?, ?, ?)",
                (username, password_hash, email, full_name)
            )
            self.conn.commit()
            
            # Create an initial empty portfolio for the user
            self.create_portfolio(username, {})
            
            return True
        except sqlite3.IntegrityError:
            # Username already exists
            return False
    
    def verify_user(self, username: str, password: str) -> bool:
        """Verify a user's credentials"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT password_hash FROM users WHERE username = ?",
            (username,)
        )
        result = cursor.fetchone()
        
        if result and result['password_hash'] == self._hash_password(password):
            return True
        return False
    
    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user information by username"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT username, email, full_name FROM users WHERE username = ?",
            (username,)
        )
        result = cursor.fetchone()
        
        return dict(result) if result else None
    
    def _hash_password(self, password: str) -> str:
        """Hash a password for storage"""
        # In a production app, you would use a better method like bcrypt
        return hashlib.sha256(password.encode()).hexdigest()
    
    # Portfolio Management Functions
    def create_portfolio(self, username: str, portfolio_data: Dict[str, Dict[str, Any]], 
                        cash_balance: float = 1000, start_date: str = "2024-01-01") -> int:
        """Create a new portfolio for a user"""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO portfolios (username, portfolio_data, cash_balance, start_date) VALUES (?, ?, ?, ?)",
            (username, json.dumps(portfolio_data), cash_balance, start_date)
        )
        self.conn.commit()
        
        return cursor.lastrowid
    
    def get_portfolio(self, username: str) -> Optional[Dict[str, Any]]:
        """Get the portfolio data for a user"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, portfolio_data, cash_balance, start_date FROM portfolios WHERE username = ?",
            (username,)
        )
        result = cursor.fetchone()
        
        if not result:
            return None
        
        portfolio = dict(result)
        # Parse the JSON data
        portfolio['portfolio_data'] = json.loads(portfolio['portfolio_data'])
        
        return portfolio
    
    def update_portfolio(self, username: str, portfolio_data: Dict[str, Dict[str, Any]]) -> bool:
        """Update a user's portfolio data"""
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE portfolios SET portfolio_data = ? WHERE username = ?",
            (json.dumps(portfolio_data), username)
        )
        self.conn.commit()
        
        return cursor.rowcount > 0
    
    def update_portfolio_settings(self, username: str, cash_balance: Optional[float] = None, 
                                start_date: Optional[str] = None) -> bool:
        """Update a user's portfolio settings"""
        updates = []
        params = []
        
        if cash_balance is not None:
            updates.append("cash_balance = ?")
            params.append(cash_balance)
        
        if start_date is not None:
            updates.append("start_date = ?")
            params.append(start_date)
        
        if not updates:
            return False
        
        cursor = self.conn.cursor()
        cursor.execute(
            f"UPDATE portfolios SET {', '.join(updates)} WHERE username = ?",
            params + [username]
        )
        self.conn.commit()
        
        return cursor.rowcount > 0
    
    # Admin Functions
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users (for admin purposes)"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT username, email, full_name FROM users")
        results = cursor.fetchall()
        
        return [dict(row) for row in results]