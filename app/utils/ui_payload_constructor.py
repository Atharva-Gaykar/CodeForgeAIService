from typing import Optional, Dict, Any

class UIPayload:
    def __init__(
        self,
        candidate_name: Optional[str],
        skill_gap_analysis_data: Optional[Dict[str, Any]],
        mermaid_code: Optional[str],
        final_roadmap: Optional[Dict[str, Any]],
    ):
        self.candidate_name = candidate_name
        self.skill_gap_analysis_data = skill_gap_analysis_data
        self.mermaid_code = mermaid_code
        self.final_roadmap = final_roadmap

    @classmethod
    def from_state(cls, state: dict) -> "UIPayload":
        return cls(
            candidate_name=state.get("candidate_name"),
            skill_gap_analysis_data=(
                state["skill_gap_analysis_data"].model_dump()
                if state.get("skill_gap_analysis_data") else None
            ),
            mermaid_code=state.get("mermaid_code"),
            final_roadmap=state.get("final_roadmap"),
        )

    def to_dict(self) -> dict:
        return {
            k: v for k, v in self.__dict__.items()
            if v is not None       # exclude None values
        }