#!/usr/bin/env python3
"""
Thai OCR Training Logs Monitor
Real-time monitoring script for SageMaker training job logs
"""

import boto3
import time
import argparse
from datetime import datetime, timezone
import sys

class SageMakerLogsMonitor:
    def __init__(self, region_name='ap-southeast-1'):
        """Initialize the logs monitor"""
        self.region_name = region_name
        try:
            self.logs_client = boto3.client('logs', region_name=region_name)
            self.sagemaker_client = boto3.client('sagemaker', region_name=region_name)
        except Exception as e:
            print(f"❌ Error initializing AWS clients: {e}")
            print("Please check your AWS credentials and try again.")
            sys.exit(1)

    def get_training_job_status(self, job_name):
        """Get current training job status"""
        try:
            response = self.sagemaker_client.describe_training_job(TrainingJobName=job_name)
            return {
                'status': response['TrainingJobStatus'],
                'secondary_status': response.get('SecondaryStatus', 'Unknown'),
                'training_time': response.get('TrainingTimeInSeconds', 0),
                'failure_reason': response.get('FailureReason', None)
            }
        except Exception as e:
            print(f"❌ Error getting training job status: {e}")
            return None

    def get_log_stream_name(self, job_name):
        """Find the log stream name for the training job"""
        try:
            # Get training job details to find the log stream
            response = self.sagemaker_client.describe_training_job(TrainingJobName=job_name)
            training_start_time = response['TrainingStartTime']
            
            # Convert to timestamp for log stream naming
            timestamp = int(training_start_time.timestamp() * 1000)
            
            # SageMaker log stream naming pattern
            log_stream_name = f"{job_name}/algo-1-{timestamp}"
            return log_stream_name
        except Exception as e:
            print(f"❌ Error finding log stream: {e}")
            return None

    def monitor_logs(self, job_name, follow=True, start_time=None):
        """Monitor training logs in real-time"""
        log_group_name = '/aws/sagemaker/TrainingJobs'
        log_stream_name = self.get_log_stream_name(job_name)
        
        if not log_stream_name:
            print(f"❌ Could not find log stream for job: {job_name}")
            return

        print(f"🔍 Monitoring logs for training job: {job_name}")
        print(f"📝 Log stream: {log_stream_name}")
        print(f"📊 Log group: {log_group_name}")
        print("=" * 80)

        next_token = None
        seen_events = set()

        # If start_time not specified, start from 10 minutes ago
        if start_time is None:
            start_time = int((datetime.now(timezone.utc).timestamp() - 600) * 1000)

        while True:
            try:
                # Get current training status
                status = self.get_training_job_status(job_name)
                if status:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"\n[{timestamp}] 📊 Status: {status['status']} | "
                          f"Secondary: {status['secondary_status']} | "
                          f"Time: {status['training_time']}s")
                    
                    # Check if training is complete
                    if not follow and status['status'] in ['Completed', 'Failed', 'Stopped']:
                        if status['failure_reason']:
                            print(f"❌ Failure Reason: {status['failure_reason']}")
                        break

                # Get log events
                kwargs = {
                    'logGroupName': log_group_name,
                    'logStreamName': log_stream_name,
                    'startTime': start_time
                }
                
                if next_token:
                    kwargs['nextToken'] = next_token

                response = self.logs_client.get_log_events(**kwargs)
                
                # Process new events
                events = response.get('events', [])
                new_events = [e for e in events if e['eventId'] not in seen_events]
                
                for event in new_events:
                    seen_events.add(event['eventId'])
                    timestamp = datetime.fromtimestamp(event['timestamp'] / 1000).strftime("%Y-%m-%d %H:%M:%S")
                    message = event['message'].strip()
                    
                    # Color code different types of messages
                    if 'ERROR' in message.upper() or 'FAILED' in message.upper():
                        print(f"🔴 [{timestamp}] {message}")
                    elif 'WARNING' in message.upper() or 'WARN' in message.upper():
                        print(f"🟡 [{timestamp}] {message}")
                    elif 'INFO' in message.upper() or 'Starting' in message:
                        print(f"🔵 [{timestamp}] {message}")
                    elif any(keyword in message for keyword in ['epoch', 'loss', 'accuracy', 'lr']):
                        print(f"📈 [{timestamp}] {message}")
                    else:
                        print(f"⚪ [{timestamp}] {message}")

                # Update start time and token for next request
                if events:
                    start_time = events[-1]['timestamp'] + 1
                next_token = response.get('nextForwardToken')

                # If not following, just show recent logs and exit
                if not follow:
                    break

                # Wait before next poll
                time.sleep(5)

            except KeyboardInterrupt:
                print("\n\n🛑 Monitoring stopped by user")
                break
            except Exception as e:
                print(f"❌ Error monitoring logs: {e}")
                if not follow:
                    break
                print("⏳ Retrying in 10 seconds...")
                time.sleep(10)

def main():
    parser = argparse.ArgumentParser(description='Monitor SageMaker training job logs')
    parser.add_argument('job_name', help='SageMaker training job name')
    parser.add_argument('--follow', '-f', action='store_true', 
                       help='Follow logs in real-time (default: show recent logs and exit)')
    parser.add_argument('--region', default='ap-southeast-1', 
                       help='AWS region (default: ap-southeast-1)')
    parser.add_argument('--minutes', type=int, default=10,
                       help='Show logs from N minutes ago (default: 10)')
    
    args = parser.parse_args()

    # Calculate start time
    start_time = int((datetime.now(timezone.utc).timestamp() - (args.minutes * 60)) * 1000)

    # Create monitor and start watching
    monitor = SageMakerLogsMonitor(region_name=args.region)
    
    print(f"🚀 Thai OCR Training Logs Monitor")
    print(f"📋 Job: {args.job_name}")
    print(f"🌍 Region: {args.region}")
    print(f"⏰ Starting from: {args.minutes} minutes ago")
    
    if args.follow:
        print("🔄 Following logs in real-time (Ctrl+C to stop)")
    else:
        print("📄 Showing recent logs")
    
    monitor.monitor_logs(args.job_name, follow=args.follow, start_time=start_time)

if __name__ == '__main__':
    main()
