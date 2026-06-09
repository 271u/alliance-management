from __future__ import annotations

from typing import List

from pydantic import BaseModel



class AllianceApiMember(BaseModel):
  uid: str
  name: str
  hq_level: int
  power: int
  power_formatted: str
  server_id: int
  current_server_id: int
  point_id: int
  rank: int
  online: bool
  join_time: int
  army_kill: int
  career_type: int
  career_level: int
  offline_time: int


class AllianceApiResponse(BaseModel):
    alliance_id: str
    member_count: int
    members_with_positions: int
    total_power: int
    total_power_formatted: str
    members: List[AllianceApiMember]
