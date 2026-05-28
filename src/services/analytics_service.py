# src/services/analytics_service.py
import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import statistics

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self):
        self.metrics = {}
        self.alert_thresholds = {
            'response_time': 1000,  # ms
            'error_rate': 0.05,     # 5%
            'order_volume': 1000,   # orders per hour
            'delivery_time': 45     # minutes
        }
        self.alerts = []
        
    async def track_order_metric(self, metric_name: str, value: float, tags: Dict = None):
        """Track order-related metrics"""
        timestamp = datetime.now()
        
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        
        self.metrics[metric_name].append({
            'value': value,
            'timestamp': timestamp,
            'tags': tags or {}
        })
        
        # Keep only last 24 hours of data
        cutoff_time = timestamp - timedelta(hours=24)
        self.metrics[metric_name] = [
            m for m in self.metrics[metric_name] 
            if m['timestamp'] > cutoff_time
        ]
        
        # Check for alerts
        await self.check_alert_conditions(metric_name, value, tags)
        
        logger.debug(f"Tracked metric: {metric_name} = {value}")
    
    async def get_system_health(self) -> Dict:
        """Get comprehensive system health report"""
        current_time = datetime.now()
        one_hour_ago = current_time - timedelta(hours=1)
        
        # Calculate key metrics
        order_volume = await self.calculate_order_volume(one_hour_ago, current_time)
        error_rate = await self.calculate_error_rate(one_hour_ago, current_time)
        avg_response_time = await self.calculate_avg_response_time(one_hour_ago, current_time)
        avg_delivery_time = await self.calculate_avg_delivery_time(one_hour_ago, current_time)
        
        # Determine overall status
        status = "healthy"
        if (error_rate > self.alert_thresholds['error_rate'] or 
            avg_response_time > self.alert_thresholds['response_time']):
            status = "degraded"
        if error_rate > 0.1:  # 10% error rate
            status = "unhealthy"
        
        return {
            'status': status,
            'timestamp': current_time.isoformat(),
            'metrics': {
                'order_volume': order_volume,
                'error_rate': error_rate,
                'avg_response_time': avg_response_time,
                'avg_delivery_time': avg_delivery_time,
                'active_users': await self.get_active_users_count(),
                'system_uptime': await self.get_system_uptime()
            },
            'alerts': self.get_recent_alerts(1),  # Last hour alerts
            'recommendations': await self.generate_recommendations()
        }
    
    async def calculate_order_volume(self, start_time: datetime, end_time: datetime) -> int:
        """Calculate order volume for time period"""
        orders = self.metrics.get('order_placed', [])
        period_orders = [
            order for order in orders 
            if start_time <= order['timestamp'] <= end_time
        ]
        return len(period_orders)
    
    async def calculate_error_rate(self, start_time: datetime, end_time: datetime) -> float:
        """Calculate error rate for time period"""
        errors = self.metrics.get('error_occurred', [])
        total_requests = self.metrics.get('request_processed', [])
        
        period_errors = [
            error for error in errors 
            if start_time <= error['timestamp'] <= end_time
        ]
        period_requests = [
            req for req in total_requests 
            if start_time <= req['timestamp'] <= end_time
        ]
        
        if not period_requests:
            return 0.0
        
        return len(period_errors) / len(period_requests)
    
    async def calculate_avg_response_time(self, start_time: datetime, end_time: datetime) -> float:
        """Calculate average response time"""
        response_times = self.metrics.get('response_time', [])
        period_times = [
            rt for rt in response_times 
            if start_time <= rt['timestamp'] <= end_time
        ]
        
        if not period_times:
            return 0.0
        
        return statistics.mean(rt['value'] for rt in period_times)
    
    async def calculate_avg_delivery_time(self, start_time: datetime, end_time: datetime) -> float:
        """Calculate average delivery time"""
        delivery_times = self.metrics.get('delivery_completed', [])
        period_times = [
            dt for dt in delivery_times 
            if start_time <= dt['timestamp'] <= end_time and 'duration' in dt['tags']
        ]
        
        if not period_times:
            return 0.0
        
        return statistics.mean(dt['tags']['duration'] for dt in period_times)
    
    async def check_alert_conditions(self, metric_name: str, value: float, tags: Dict):
        """Check if metric triggers any alerts"""
        threshold = self.alert_thresholds.get(metric_name)
        
        if threshold and value > threshold:
            alert = {
                'type': metric_name,
                'value': value,
                'threshold': threshold,
                'timestamp': datetime.now(),
                'severity': 'high' if value > threshold * 1.5 else 'medium',
                'message': f"{metric_name} exceeded threshold: {value} > {threshold}"
            }
            
            self.alerts.append(alert)
            await self.notify_alert(alert)
            
            logger.warning(f"Alert triggered: {alert['message']}")
    
    async def notify_alert(self, alert: Dict):
        """Notify about system alert"""
        # In production, this would send email, Slack message, etc.
        logger.error(f"SYSTEM ALERT: {alert['message']}")
    
    def get_recent_alerts(self, hours: int = 1) -> List[Dict]:
        """Get recent alerts from the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [alert for alert in self.alerts if alert['timestamp'] > cutoff_time]
    
    async def get_active_users_count(self) -> int:
        """Get count of active users in last 15 minutes"""
        cutoff_time = datetime.now() - timedelta(minutes=15)
        user_activities = self.metrics.get('user_activity', [])
        
        active_users = set()
        for activity in user_activities:
            if activity['timestamp'] > cutoff_time:
                user_id = activity['tags'].get('user_id')
                if user_id:
                    active_users.add(user_id)
        
        return len(active_users)
    
    async def get_system_uptime(self) -> str:
        """Get system uptime as string"""
        # In production, this would calculate actual uptime
        return "99.95%"
    
    async def generate_recommendations(self) -> List[str]:
        """Generate system recommendations based on metrics"""
        recommendations = []
        # Avoid recursive health evaluation by computing recommendations from
        # the underlying metric values directly.
        current_time = datetime.now()
        one_hour_ago = current_time - timedelta(hours=1)
        metrics = {
            'error_rate': await self.calculate_error_rate(one_hour_ago, current_time),
            'avg_response_time': await self.calculate_avg_response_time(one_hour_ago, current_time),
            'avg_delivery_time': await self.calculate_avg_delivery_time(one_hour_ago, current_time)
        }
        
        if metrics['error_rate'] > 0.03:
            recommendations.append("Investigate increased error rate in order processing")
        
        if metrics['avg_response_time'] > 800:
            recommendations.append("Optimize API response times for better user experience")
        
        if metrics['avg_delivery_time'] > 40:
            recommendations.append("Review delivery partner allocation and routes")
        
        if not recommendations:
            recommendations.append("System performing within expected parameters")
        
        return recommendations
    
    async def get_business_insights(self) -> Dict:
        """Get business insights and analytics"""
        current_time = datetime.now()
        yesterday = current_time - timedelta(days=1)
        last_week = current_time - timedelta(days=7)
        
        # Calculate business metrics
        today_orders = await self.calculate_order_volume(
            current_time.replace(hour=0, minute=0, second=0), current_time
        )
        yesterday_orders = await self.calculate_order_volume(
            yesterday.replace(hour=0, minute=0, second=0), yesterday
        )
        week_orders = await self.calculate_order_volume(last_week, current_time)
        
        # Calculate revenue (simplified)
        avg_order_value = 25.0  # In production, this would be calculated from actual data
        today_revenue = today_orders * avg_order_value
        week_revenue = week_orders * avg_order_value
        
        # Popular cuisines
        popular_cuisines = await self.get_popular_cuisines(last_week, current_time)
        
        return {
            'orders_today': today_orders,
            'orders_yesterday': yesterday_orders,
            'order_growth': ((today_orders - yesterday_orders) / yesterday_orders * 100) 
                           if yesterday_orders > 0 else 0,
            'revenue_today': today_revenue,
            'revenue_week': week_revenue,
            'popular_cuisines': popular_cuisines,
            'peak_hours': await self.get_peak_hours(last_week, current_time),
            'customer_satisfaction': await self.get_customer_satisfaction(last_week, current_time)
        }
    
    async def get_popular_cuisines(self, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Get popular cuisines for time period"""
        # In production, this would analyze order data
        return [
            {'cuisine': 'Italian', 'orders': 45, 'growth': 12},
            {'cuisine': 'Indian', 'orders': 38, 'growth': 8},
            {'cuisine': 'Chinese', 'orders': 32, 'growth': 15},
            {'cuisine': 'Mexican', 'orders': 28, 'growth': 5},
            {'cuisine': 'American', 'orders': 25, 'growth': -2}
        ]
    
    async def get_peak_hours(self, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Get peak ordering hours"""
        # In production, this would analyze order timestamps
        return [
            {'hour': '12:00-13:00', 'orders': 120},
            {'hour': '18:00-19:00', 'orders': 150},
            {'hour': '19:00-20:00', 'orders': 145},
            {'hour': '13:00-14:00', 'orders': 95}
        ]
    
    async def get_customer_satisfaction(self, start_time: datetime, end_time: datetime) -> float:
        """Calculate customer satisfaction score"""
        # In production, this would analyze ratings and reviews
        return 4.5  # Out of 5
