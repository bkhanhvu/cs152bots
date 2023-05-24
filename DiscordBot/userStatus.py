from __future__ import annotations
import dataclasses

@dataclasses.dataclass

class UserStatus:
  # Since we aren't really implementing bans, a flag seems good enough
  # In the real world we'd probably have a ban expiry time (instead?)
  isBanned : bool = False
  strikeCounter : int = 0

# User id to status
userStatuses : dict[str, UserStatus] = {}