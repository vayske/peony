from graia.ariadne.model import Group, Member
from graia.broadcast.exceptions import ExecutionStop
import json
import os

COMMAND_HEADS = r"[/$#!%-.?]"

def require_group(*group_id: int):
    async def wrapper(group: Group):
        if group.id not in group_id:
            raise ExecutionStop
    return wrapper

def require_member(member_id: int):
    async def wrapper(member: Member):
        if member.id != member_id:
            raise ExecutionStop
    return wrapper

def create_json(file_path):
    if os.path.exists(file_path):
        return
    with open(file_path, 'w') as file:
        json.dump({}, file, ensure_ascii=False, sort_keys=True, indent=2)

def create_description(title, commands, examples):
    description = f"{title}\n" \
                  "指令:\n" \
                  f"{commands}" \
                  "使用例:\n" \
                  f"{examples}"
    return description
