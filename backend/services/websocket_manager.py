from fastapi import WebSocket
from typing import List, Dict
import json
from datetime import datetime

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_data: Dict[WebSocket, Dict] = {}
    
    async def connect(self, websocket: WebSocket):
        """Accept and store WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_data[websocket] = {
            'connected_at': datetime.utcnow().isoformat(),
            'messages_sent': 0,
            'messages_received': 0
        }
        print(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.connection_data:
            del self.connection_data[websocket]
        print(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific connection"""
        try:
            await websocket.send_text(message)
            if websocket in self.connection_data:
                self.connection_data[websocket]['messages_sent'] += 1
        except Exception as e:
            print(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: str):
        """Broadcast message to all connections"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
                if connection in self.connection_data:
                    self.connection_data[connection]['messages_sent'] += 1
            except Exception as e:
                print(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)
    
    def active_connections_count(self) -> int:
        """Get count of active connections"""
        return len(self.active_connections)
    
    async def send_valuation_update(self, property_id: str, valuation: Dict):
        """Send valuation update to all clients"""
        message = json.dumps({
            'type': 'valuation_update',
            'data': {
                'property_id': property_id,
                'valuation': valuation,
                'timestamp': datetime.utcnow().isoformat()
            }
        })
        await self.broadcast(message)
    
    async def send_market_update(self, market_data: Dict):
        """Send market update to all clients"""
        message = json.dumps({
            'type': 'market_update',
            'data': {
                **market_data,
                'timestamp': datetime.utcnow().isoformat()
            }
        })
        await self.broadcast(message)
    
    async def send_model_update(self, model_metrics: Dict):
        """Send model performance update"""
        message = json.dumps({
            'type': 'model_update',
            'data': {
                'metrics': model_metrics,
                'timestamp': datetime.utcnow().isoformat()
            }
        })
        await self.broadcast(message)
    
    def get_connection_stats(self) -> Dict:
        """Get statistics about WebSocket connections"""
        total_messages_sent = sum(
            data['messages_sent'] 
            for data in self.connection_data.values()
        )
        total_messages_received = sum(
            data['messages_received'] 
            for data in self.connection_data.values()
        )
        
        return {
            'active_connections': self.active_connections_count(),
            'total_messages_sent': total_messages_sent,
            'total_messages_received': total_messages_received,
            'connections': [
                {
                    'connected_at': data['connected_at'],
                    'messages_sent': data['messages_sent'],
                    'messages_received': data['messages_received']
                }
                for data in self.connection_data.values()
            ]
        }