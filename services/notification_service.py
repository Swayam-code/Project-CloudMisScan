from typing import Dict, Any, List, Optional
import requests
import json
import logging
from datetime import datetime

class NotificationService:
    def __init__(self, slack_webhook_url: Optional[str] = None, teams_webhook_url: Optional[str] = None):
        """Initialize notification service with webhook URLs"""
        self.slack_webhook_url = slack_webhook_url
        self.teams_webhook_url = teams_webhook_url
        self.logger = logging.getLogger(__name__)

    def send_slack_notification(self, message: Dict[str, Any]) -> bool:
        """Send notification to Slack"""
        if not self.slack_webhook_url:
            self.logger.warning("Slack webhook URL not configured")
            return False

        try:
            response = requests.post(
                self.slack_webhook_url,
                json=message,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            return True
        except Exception as e:
            self.logger.error(f"Failed to send Slack notification: {str(e)}")
            return False

    def send_teams_notification(self, message: Dict[str, Any]) -> bool:
        """Send notification to Microsoft Teams"""
        if not self.teams_webhook_url:
            self.logger.warning("Teams webhook URL not configured")
            return False

        try:
            # Convert message to Teams format
            teams_message = {
                "@type": "MessageCard",
                "@context": "http://schema.org/extensions",
                "summary": message.get("summary", "AWS Scan Results"),
                "themeColor": "0076D7",
                "sections": [
                    {
                        "activityTitle": message.get("title", "AWS Scan Results"),
                        "activitySubtitle": message.get("subtitle", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                        "facts": [
                            {"name": k, "value": v}
                            for k, v in message.get("fields", {}).items()
                        ],
                        "markdown": True
                    }
                ]
            }

            response = requests.post(
                self.teams_webhook_url,
                json=teams_message,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            return True
        except Exception as e:
            self.logger.error(f"Failed to send Teams notification: {str(e)}")
            return False

    def notify_scan_results(self, scan_results: Dict[str, Any], notification_type: str = "both") -> bool:
        """Send scan results notification to configured platforms"""
        success = True
        
        # Calculate summary statistics
        total_issues = sum(
            len(resource.get("misconfigurations", []))
            for service in ["s3", "ec2", "iam", "rds", "network"]
            for resource in scan_results.get(service, [])
        )
        
        high_severity = sum(
            1 for service in ["s3", "ec2", "iam", "rds", "network"]
            for resource in scan_results.get(service, [])
            for issue in resource.get("misconfigurations", [])
            if issue.get("severity") == "HIGH"
        )
        
        # Get compliance scores
        compliance_scores = {}
        if "compliance" in scan_results:
            for framework in ["cis", "nist", "pci"]:
                if framework in scan_results["compliance"]:
                    controls = scan_results["compliance"][framework]["controls"]
                    total = len(controls)
                    passed = len([c for c in controls if c["status"] == "PASS"])
                    compliance_scores[framework.upper()] = f"{(passed/total*100):.1f}%" if total > 0 else "N/A"

        # Prepare message for both platforms
        message = {
            "title": "AWS Security Scan Results",
            "subtitle": f"Scan completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "summary": "AWS Security Scan Results",
            "fields": {
                "Total Issues": total_issues,
                "High Severity Issues": high_severity,
                **compliance_scores
            }
        }

        # Send to Slack
        if notification_type in ["slack", "both"]:
            slack_message = {
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": message["title"]
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*{k}:*\n{v}"
                            } for k, v in message["fields"].items()
                        ]
                    }
                ]
            }
            if not self.send_slack_notification(slack_message):
                success = False

        # Send to Teams
        if notification_type in ["teams", "both"]:
            if not self.send_teams_notification(message):
                success = False

        return success

    def notify_changes(self, changes: List[Dict[str, Any]], notification_type: str = "both") -> bool:
        """Send notification about detected changes"""
        if not changes:
            return True

        # Group changes by type
        changes_summary = {
            "new_resource": [],
            "new_issues": [],
            "removed_resource": [],
            "resolved_issues": []
        }
        
        for change in changes:
            change_type = change.get("type")
            if change_type in changes_summary:
                changes_summary[change_type].append(
                    f"{change['service']}: {change['resource_id']} "
                    f"({change.get('issues', 0)} issues)"
                )

        # Prepare message
        message = {
            "title": "AWS Security Changes Detected",
            "subtitle": f"Changes as of {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "summary": "AWS Security Changes",
            "fields": {
                "New Resources": "\n".join(changes_summary["new_resource"]) or "None",
                "New Issues": "\n".join(changes_summary["new_issues"]) or "None",
                "Removed Resources": "\n".join(changes_summary["removed_resource"]) or "None",
                "Resolved Issues": "\n".join(changes_summary["resolved_issues"]) or "None"
            }
        }

        success = True

        # Send to Slack
        if notification_type in ["slack", "both"]:
            slack_message = {
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": message["title"]
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*{k}:*\n{v}"
                            } for k, v in message["fields"].items()
                        ]
                    }
                ]
            }
            if not self.send_slack_notification(slack_message):
                success = False

        # Send to Teams
        if notification_type in ["teams", "both"]:
            if not self.send_teams_notification(message):
                success = False

        return success
