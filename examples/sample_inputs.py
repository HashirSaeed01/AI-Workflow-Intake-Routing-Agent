"""Realistic messy incoming messages for demo and testing."""

SAMPLE_MESSAGES = [
    {
        "label": "Customer billing dispute (email)",
        "source": "email",
        "metadata": {"from": "sarah.chen@northwind.io", "subject": "Wrong charge???"},
        "text": """Hi Rozeta Labs team,

This is Sarah Chen from Northwind Analytics. We were charged $4,800 on invoice #INV-9921
but our enterprise plan should be $3,200/month. This happened twice last week and I need
this fixed ASAP before our finance close on Friday.

Can someone review and issue a refund for the overcharge?

Thanks,
Sarah""",
    },
    {
        "label": "Sales enterprise inquiry (CRM note)",
        "source": "crm_note",
        "metadata": {"rep": "jordan", "account": "Acme Robotics"},
        "text": """Inbound from VP Eng at Acme Robotics — they want pricing for 200-seat
enterprise deployment, SSO, and a technical demo next Tuesday. Mentioned competitor quote
from DataFlow Inc. High intent; asked for annual contract options and onboarding timeline.""",
    },
    {
        "label": "Internal ops access request (Slack paste)",
        "source": "slack",
        "metadata": {"channel": "#internal-ops", "requester": "devon.park"},
        "text": """@ops-team need access provisioning for new vendor onboarding workflow in
Notion + Jira for Q3 headcount plan. 3 contractors start Monday. Not urgent but need done
by EOD tomorrow. Internal request — no customer impact.""",
    },
    {
        "label": "Production API outage (support ticket)",
        "source": "ticket",
        "metadata": {"ticket_id": "TKT-44102", "severity": "P1"},
        "text": """URGENT — Production API returning 500 errors since 09:14 UTC.
Endpoint: POST /v2/workflows/run — customers cannot execute automations.
Error spike in dashboard. Possible regression after last night's deploy v2.14.3.
Need engineering on-call immediately.""",
    },
]
