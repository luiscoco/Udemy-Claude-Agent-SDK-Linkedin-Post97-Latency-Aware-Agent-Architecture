"""Lesson-specific workflow. Read this file before the execution adapter."""
from __future__ import annotations
import asyncio
import json
from pathlib import Path
from runtime import atomic_json, contained_path, in_process_tool

async def run(agent, data):
    if data['deadline_seconds'] <= 0 or data['simulated_delay_seconds'] < 0:
        raise ValueError('Invalid latency configuration')
    async def slow_stage():
        if not agent.live:
            await asyncio.sleep(data['simulated_delay_seconds'])
        return await agent.ask('fresh_answer', 'Provide a concise policy summary.', {}, 'Fresh fixture response.')
    try:
        answer = await asyncio.wait_for(slow_stage(), timeout=data['deadline_seconds'])
        return {'source': 'fresh_run', 'answer': answer, 'timed_out': False}
    except asyncio.TimeoutError:
        agent.event('deadline_exceeded', stage='fresh_answer')
        return {'source': 'cached_fallback', 'answer': data['cached_answer'], 'cached_at': data['cached_at'], 'timed_out': True}
