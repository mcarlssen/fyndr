#!/usr/bin/env python3
"""
Event Analysis Tool for FYNDR Simulations

Analyzes and displays game events to help correlate player activity with events.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any
from collections import defaultdict, Counter


class EventAnalyzer:
    """Analyzes game events from simulation data"""
    
    def __init__(self, simulation_file: str):
        self.simulation_file = simulation_file
        self.data = self.load_simulation_data()
        self.events = self.data.get('game_events', [])
        self.daily_stats = self.data.get('daily_stats', [])
    
    def load_simulation_data(self) -> Dict[str, Any]:
        """Load simulation data from JSON file"""
        with open(self.simulation_file, 'r') as f:
            return json.load(f)
    
    def get_event_summary(self) -> Dict[str, Any]:
        """Get summary of all events"""
        event_counts = Counter(event['event_type'] for event in self.events)
        
        summary = {
            'total_events': len(self.events),
            'event_types': dict(event_counts),
            'simulation_days': len(self.daily_stats),
            'events_per_day': len(self.events) / len(self.daily_stats) if self.daily_stats else 0
        }
        
        return summary
    
    def get_events_by_day(self) -> Dict[int, List[Dict]]:
        """Get all events grouped by day"""
        events_by_day = defaultdict(list)
        
        for event in self.events:
            day = event['day']
            events_by_day[day].append(event)
        
        return dict(events_by_day)
    
    def get_event_correlations(self) -> Dict[str, Any]:
        """Analyze correlations between events and player activity"""
        correlations = {}
        
        # Group events by type
        events_by_type = defaultdict(list)
        for event in self.events:
            events_by_type[event['event_type']].append(event)
        
        # Analyze each event type
        for event_type, events in events_by_type.items():
            if not events:
                continue
                
            # Get days when this event occurred
            event_days = [event['day'] for event in events]
            
            # Get activity metrics for those days
            activity_metrics = []
            for day in event_days:
                if day < len(self.daily_stats):
                    stats = self.daily_stats[day]
                    activity_metrics.append({
                        'day': day,
                        'active_players': stats.get('active_players', 0),
                        'total_scans': stats.get('total_scans', 0),
                        'total_revenue': stats.get('total_revenue', 0),
                        'growth_rate': stats.get('growth_rate', 0)
                    })
            
            correlations[event_type] = {
                'event_count': len(events),
                'affected_players': sum(event.get('affected_players', 0) for event in events),
                'affected_stickers': sum(event.get('affected_stickers', 0) for event in events),
                'activity_metrics': activity_metrics
            }
        
        return correlations
    
    def get_timeline_analysis(self) -> List[Dict]:
        """Get timeline of events and their impacts"""
        timeline = []
        
        for day_stats in self.daily_stats:
            day = day_stats['day']
            
            # Get events for this day
            day_events = [event for event in self.events if event['day'] == day]
            
            timeline_entry = {
                'day': day,
                'active_players': day_stats.get('active_players', 0),
                'total_scans': day_stats.get('total_scans', 0),
                'total_revenue': day_stats.get('total_revenue', 0),
                'growth_rate': day_stats.get('growth_rate', 0),
                'events': day_events,
                'active_events': day_stats.get('active_events', []),
                'event_impacts': day_stats.get('event_impacts', {})
            }
            
            timeline.append(timeline_entry)
        
        return timeline
    
    def find_high_impact_days(self, metric: str = 'total_scans', threshold_percentile: float = 90) -> List[Dict]:
        """Find days with high activity and their associated events"""
        # Get all values for the metric
        values = [day_stats.get(metric, 0) for day_stats in self.daily_stats]
        if not values:
            return []
        
        # Calculate threshold
        sorted_values = sorted(values, reverse=True)
        threshold_index = int(len(sorted_values) * (100 - threshold_percentile) / 100)
        threshold = sorted_values[threshold_index] if threshold_index < len(sorted_values) else sorted_values[-1]
        
        # Find high-impact days
        high_impact_days = []
        for day_stats in self.daily_stats:
            if day_stats.get(metric, 0) >= threshold:
                day = day_stats['day']
                day_events = [event for event in self.events if event['day'] == day]
                
                high_impact_days.append({
                    'day': day,
                    'metric_value': day_stats.get(metric, 0),
                    'events': day_events,
                    'active_events': day_stats.get('active_events', []),
                    'event_impacts': day_stats.get('event_impacts', {})
                })
        
        return sorted(high_impact_days, key=lambda x: x['metric_value'], reverse=True)
    
    def generate_event_report(self) -> str:
        """Generate a comprehensive event analysis report"""
        report = []
        
        # Header
        report.append("🎮 FYNDR SIMULATION EVENT ANALYSIS REPORT")
        report.append("=" * 60)
        report.append(f"Simulation File: {os.path.basename(self.simulation_file)}")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Event Summary
        summary = self.get_event_summary()
        report.append("📊 EVENT SUMMARY")
        report.append("-" * 20)
        report.append(f"Total Events: {summary['total_events']}")
        report.append(f"Simulation Days: {summary['simulation_days']}")
        report.append(f"Events per Day: {summary['events_per_day']:.2f}")
        report.append("")
        
        report.append("Event Types:")
        for event_type, count in summary['event_types'].items():
            report.append(f"  {event_type}: {count}")
        report.append("")
        
        # Event Correlations
        correlations = self.get_event_correlations()
        report.append("🔗 EVENT CORRELATIONS")
        report.append("-" * 25)
        
        for event_type, data in correlations.items():
            report.append(f"\n{event_type.upper()}:")
            report.append(f"  Total Events: {data['event_count']}")
            report.append(f"  Affected Players: {data['affected_players']}")
            report.append(f"  Affected Stickers: {data['affected_stickers']}")
            
            if data['activity_metrics']:
                avg_players = sum(m['active_players'] for m in data['activity_metrics']) / len(data['activity_metrics'])
                avg_scans = sum(m['total_scans'] for m in data['activity_metrics']) / len(data['activity_metrics'])
                avg_revenue = sum(m['total_revenue'] for m in data['activity_metrics']) / len(data['activity_metrics'])
                
                report.append(f"  Avg Players on Event Days: {avg_players:.1f}")
                report.append(f"  Avg Scans on Event Days: {avg_scans:.1f}")
                report.append(f"  Avg Revenue on Event Days: ${avg_revenue:.2f}")
        
        # High Impact Days
        high_impact_days = self.find_high_impact_days('total_scans', 90)
        if high_impact_days:
            report.append("\n🚀 HIGH IMPACT DAYS (Top 10% by Scans)")
            report.append("-" * 40)
            
            for day_data in high_impact_days[:10]:  # Top 10
                report.append(f"\nDay {day_data['day']}: {day_data['metric_value']} scans")
                if day_data['events']:
                    report.append("  Events:")
                    for event in day_data['events']:
                        report.append(f"    - {event['description']}")
                if day_data['active_events']:
                    report.append(f"  Active Events: {', '.join(day_data['active_events'])}")
        
        # Timeline Analysis
        timeline = self.get_timeline_analysis()
        report.append("\n📅 TIMELINE ANALYSIS")
        report.append("-" * 20)
        
        # Find days with most events
        eventful_days = [(day_data['day'], len(day_data['events'])) for day_data in timeline if day_data['events']]
        eventful_days.sort(key=lambda x: x[1], reverse=True)
        
        if eventful_days:
            report.append("Most Eventful Days:")
            for day, event_count in eventful_days[:5]:
                report.append(f"  Day {day}: {event_count} events")
        
        return "\n".join(report)
    
    def save_event_timeline(self, output_file: str = None):
        """Save detailed event timeline to JSON file"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"event_timeline_{timestamp}.json"
        
        timeline = self.get_timeline_analysis()
        
        with open(output_file, 'w') as f:
            json.dump({
                'simulation_file': self.simulation_file,
                'generated_at': datetime.now().isoformat(),
                'timeline': timeline,
                'event_summary': self.get_event_summary(),
                'correlations': self.get_event_correlations()
            }, f, indent=2)
        
        print(f"Event timeline saved to: {output_file}")
        return output_file


def main():
    """Main function"""
    print("🎮 FYNDR Event Analysis Tool")
    print("=" * 40)
    
    # Find simulation files in organized directory structure
    simulation_files = []
    
    # Check simulations directory
    if os.path.exists('simulations'):
        for sim_dir in os.listdir('simulations'):
            sim_path = os.path.join('simulations', sim_dir)
            if os.path.isdir(sim_path):
                for file in os.listdir(sim_path):
                    if file.startswith('fyndr_life_sim_') and file.endswith('.json'):
                        simulation_files.append(os.path.join(sim_path, file))
    
    # Also check current directory for backward compatibility
    for file in os.listdir('.'):
        if file.startswith('fyndr_life_sim_') and file.endswith('.json'):
            simulation_files.append(file)
    
    if not simulation_files:
        print("❌ No simulation files found!")
        return
    
    # Use the most recent simulation file
    latest_file = max(simulation_files, key=os.path.getctime)
    print(f"📁 Analyzing: {latest_file}")
    
    # Analyze events
    analyzer = EventAnalyzer(latest_file)
    
    # Generate report
    report = analyzer.generate_event_report()
    print("\n" + report)
    
    # Save detailed timeline
    timeline_file = analyzer.save_event_timeline()
    
    print(f"\n✅ Analysis complete!")
    print(f"📄 Detailed timeline saved to: {timeline_file}")


if __name__ == "__main__":
    main()
