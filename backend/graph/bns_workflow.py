"""LangGraph workflow for BNS section prediction

Workflow:
1. Refine crime description (Agent 0)
2. Predict BNS sections (Agent 1)
3. Return predictions
"""

from typing import TypedDict, List, Dict, Optional
from langgraph.graph import StateGraph, END
from agents.crime_refiner import CrimeRefinerAgent
from agents.bns_predictor import BNSPredictorAgent


# Define state
class BNSWorkflowState(TypedDict):
    """State passed between nodes"""
    raw_description: str
    refined_description: str
    predictions: List[Dict]
    error: Optional[str]


# Initialize agents
refiner = CrimeRefinerAgent()
predictor = BNSPredictorAgent()


# Node functions
def refine_description(state: BNSWorkflowState) -> BNSWorkflowState:
    """Node 1: Refine crime description"""
    print("📝 Refining description...")

    refined = refiner.refine(state["raw_description"])

    return {
        **state,
        "refined_description": refined
    }


def predict_sections(state: BNSWorkflowState) -> BNSWorkflowState:
    """Node 2: Predict BNS sections"""
    print("🔍 Predicting BNS sections...")

    predictions = predictor.predict(state["refined_description"])

    return {
        **state,
        "predictions": predictions
    }


# Build graph
def create_bns_workflow():
    """Create and compile the BNS prediction workflow"""

    workflow = StateGraph(BNSWorkflowState)

    # Add nodes
    workflow.add_node("refine", refine_description)
    workflow.add_node("predict", predict_sections)

    # Add edges
    workflow.set_entry_point("refine")
    workflow.add_edge("refine", "predict")
    workflow.add_edge("predict", END)

    # Compile
    return workflow.compile()


# Main prediction function
def predict_bns(crime_description: str) -> Dict:
    """
    Main entry point for BNS prediction.

    Args:
        crime_description: Raw crime description

    Returns:
        {
            "raw_description": str,
            "refined_description": str,
            "predictions": [...]
        }
    """
    # Create workflow
    app = create_bns_workflow()

    # Initial state
    initial_state = {
        "raw_description": crime_description,
        "refined_description": "",
        "predictions": [],
        "error": None
    }

    # Run workflow
    try:
        result = app.invoke(initial_state)
        return result
    except Exception as e:
        return {
            **initial_state,
            "error": str(e)
        }
