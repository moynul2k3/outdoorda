from fastapi import APIRouter, Depends, Query, HTTPException
from app.auth import role_required
from typing import Any
from tortoise.timezone import now
from applications.user.models import User
from routes.user.agent_performance import call_stats, appointment_stats, conversation_stat
from applications.user.models import UserRole

router = APIRouter(prefix="/export", tags=["Export Report"])

from datetime import datetime, timedelta
from tortoise.timezone import make_aware

async def get_agent_performance_by_date(agent_id: str, date):
    start = make_aware(datetime.combine(date, datetime.min.time()))
    end = start + timedelta(days=1)

    call = await call_stats(agent_id, start, end)
    appointment = await appointment_stats(agent_id, start, end)

    conversation = await conversation_stat(agent_id, start, end)

    return {
        "call": call["total"],
        "call_rate": call["rate"],
        "missed_calls": call["missed"],
        "avg_call_time": call["avg_time"],

        "appointment": appointment["total"],
        "appointment_rate": appointment["rate"],

        # placeholders
        "conversation_rate": conversation["rate"],
        "message_sent": conversation["total"],
    }


def get_date_range(period: str):
    today = now().date()

    if period == "daily":
        return [today]

    if period == "weekly":
        return [today - timedelta(days=i) for i in range(7)]

    if period == "yearly":
        return [today - timedelta(days=i) for i in range(365)]

    raise ValueError("Invalid period")



async def serialize_agent_performance_table(
    export_type:str = "agent_performance",
    period: str = "daily",
    agent_id: str | None = None,
) -> list[dict[str, Any]]:

    rows: list[dict[str, Any]] = []

    agents_qs = User.filter(role=UserRole.AGENT)
    if agent_id:
        agents_qs = agents_qs.filter(id=agent_id)

    agents = await agents_qs.all()
    dates = get_date_range(period)

    for agent in agents:
        for date in dates:
            perf = await get_agent_performance_by_date(agent.id, date)
            row = {
                "date": date.isoformat(),
                "agent_id": str(agent.id),
                "agent_name": agent.name,

                "appointments": perf["appointment"],
                "appointment_rate": perf["appointment_rate"],

                "conversation_rate": perf["conversation_rate"],
                "message_sent": perf["message_sent"],
            }

            if export_type == "call_analytics":
                row.update({
                    "calls": perf["call"],
                    "call_rate": perf["call_rate"],
                    "missed_calls": perf["missed_calls"],
                    "avg_call_time": perf["avg_call_time"],
                })

            rows.append(row)
    rows.sort(key=lambda x: x["date"], reverse=True)
    return rows

@router.get(
    "/export",
    dependencies=[Depends(role_required(UserRole.MANAGER, isGranted=True))],
)
async def export_agent_performance_table(
    export_type: str = Query("agent_performance", description="agent_performance | call_analytics"),
    period: str = Query("daily", description="daily | weekly | yearly"),
    agent_id: str | None = None,
):
    if period not in {"daily", "weekly", "yearly"}:
        raise HTTPException(400, "Invalid period")

    if export_type not in {"agent_performance", "call_analytics"}:
        raise HTTPException(400, "Invalid Export Type")

    return {
        "count": 0,
        "period": period,
        "results": await serialize_agent_performance_table(
            export_type=export_type,
            period=period,
            agent_id=agent_id,
        ),
    }