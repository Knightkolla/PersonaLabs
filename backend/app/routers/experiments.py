from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.database import get_db, ExperimentDB
from app.models import (
    CreateExperimentRequest, ExperimentResponse, Experiment, 
    FeatureDescription, SimulationResponse, AggregatedInsights,
    CompanyContext, SyntheticPersona, SimulationDecision
)
from app.services.company_processor import CompanyContextProcessor
from app.services.persona_generator import PersonaGenerationEngine
from app.services.simulation_engine import SimulationEngine
from app.services.aggregation_layer import AggregationLayer
import uuid
import json
from datetime import datetime
from typing import List

router = APIRouter(prefix="/experiments", tags=["experiments"])

def _serialize_model(model_obj):
    """Helper to serialize Pydantic model to JSON string"""
    if model_obj is None:
        return None
    return model_obj.model_dump_json()

def _deserialize_model(json_str, model_class):
    """Helper to deserialize JSON string to Pydantic model"""
    if not json_str:
        return None
    return model_class.model_validate_json(json_str)

def _deserialize_list(json_str, model_class):
    """Helper to deserialize JSON list string to list of Pydantic models"""
    if not json_str:
        return []
    items = json.loads(json_str)
    return [model_class.model_validate(item) for item in items]

@router.get("/", response_model=List[Experiment])
async def list_experiments(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """List all experiments (summary view)"""
    experiments_db = db.query(ExperimentDB).order_by(ExperimentDB.updated_at.desc()).offset(skip).limit(limit).all()
    
    results = []
    for exp_db in experiments_db:
        try:
            results.append(Experiment(
                id=exp_db.id,
                user_id=exp_db.user_id,
                created_at=exp_db.created_at,
                updated_at=exp_db.updated_at,
                company_context=_deserialize_model(exp_db.company_context, CompanyContext),
                feature_description=_deserialize_model(exp_db.feature_description, FeatureDescription),
                personas=_deserialize_list(exp_db.personas, SyntheticPersona),
                simulation_results=_deserialize_list(exp_db.simulation_results, SimulationResponse),
                aggregated_insights=_deserialize_model(exp_db.aggregated_insights, AggregatedInsights),
                is_public=exp_db.is_public or False,
                share_token=exp_db.share_token
            ))
        except Exception as e:
            print(f"Error parsing experiment {exp_db.id}: {e}")
            continue
            
    return results

@router.post("/", response_model=ExperimentResponse)
async def create_experiment(
    request: CreateExperimentRequest,
    db: Session = Depends(get_db)
):
    """Create a new experiment with company context and feature description"""
    try:
        # Generate unique experiment ID
        experiment_id = str(uuid.uuid4())
        
        # Process company context
        processor = CompanyContextProcessor()
        company_context = await processor.process_company_input(request.company_input)
        
        # Generate personas
        persona_engine = PersonaGenerationEngine()
        personas = await persona_engine.generate_personas(company_context)
        
        # Create DB object
        # Note: We store JSON strings in the DB
        import json
        
        db_experiment = ExperimentDB(
            id=experiment_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            company_context=company_context.model_dump_json(),
            feature_description=request.feature_description.model_dump_json(),
            personas=json.dumps([p.model_dump() for p in personas]),
            simulation_results="[]",
            aggregated_insights=None,
            is_public=False
        )
        
        db.add(db_experiment)
        db.commit()
        db.refresh(db_experiment)
        
        # Construct response Pydantic object
        experiment = Experiment(
            id=experiment_id,
            created_at=db_experiment.created_at,
            updated_at=db_experiment.updated_at,
            company_context=company_context,
            feature_description=request.feature_description,
            personas=personas,
            simulation_results=[],
            aggregated_insights=None,
            is_public=False
        )
        
        return ExperimentResponse(
            experiment=experiment,
            status="created",
            message="Experiment created successfully. Ready for simulation."
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{experiment_id}", response_model=ExperimentResponse)
async def get_experiment(experiment_id: str, db: Session = Depends(get_db)):
    """Get experiment by ID"""
    exp_db = db.query(ExperimentDB).filter(ExperimentDB.id == experiment_id).first()
    
    if not exp_db:
        raise HTTPException(status_code=404, detail="Experiment not found")
        
    try:
        experiment = Experiment(
            id=exp_db.id,
            user_id=exp_db.user_id,
            created_at=exp_db.created_at,
            updated_at=exp_db.updated_at,
            company_context=_deserialize_model(exp_db.company_context, CompanyContext),
            feature_description=_deserialize_model(exp_db.feature_description, FeatureDescription),
            personas=_deserialize_list(exp_db.personas, SyntheticPersona),
            simulation_results=_deserialize_list(exp_db.simulation_results, SimulationResponse),
            aggregated_insights=_deserialize_model(exp_db.aggregated_insights, AggregatedInsights),
            is_public=exp_db.is_public or False,
            share_token=exp_db.share_token
        )
        
        return ExperimentResponse(
            experiment=experiment,
            status="loaded",
            message="Experiment retrieved successfully"
        )
    except Exception as e:
        print(f"Error parsing experiment: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error retrieveing experiment data")

@router.post("/{experiment_id}/simulate", response_model=ExperimentResponse)
async def run_simulation(experiment_id: str, db: Session = Depends(get_db)):
    """Run simulation for an experiment"""
    exp_db = db.query(ExperimentDB).filter(ExperimentDB.id == experiment_id).first()
    
    if not exp_db:
        raise HTTPException(status_code=404, detail="Experiment not found")
        
    try:
        # Deserialize data needed for simulation
        personas = _deserialize_list(exp_db.personas, SyntheticPersona)
        feature = _deserialize_model(exp_db.feature_description, FeatureDescription)
        
        if not personas or not feature:
            raise HTTPException(status_code=400, detail="Experiment missing personas or feature description")
            
        # Run simulation
        simulation_engine = SimulationEngine()
        results = await simulation_engine.simulate_batch_reactions(personas, feature)
        
        # Aggregate results
        aggregation_layer = AggregationLayer()
        insights = aggregation_layer.aggregate_results(results, personas)
        
        # Update DB
        exp_db.simulation_results = json.dumps([r.model_dump() for r in results], default=str)
        exp_db.aggregated_insights = insights.model_dump_json()
        exp_db.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(exp_db)
        
        # Reconstruct response
        experiment = Experiment(
            id=exp_db.id,
            user_id=exp_db.user_id,
            created_at=exp_db.created_at,
            updated_at=exp_db.updated_at,
            company_context=_deserialize_model(exp_db.company_context, CompanyContext),
            feature_description=feature,
            personas=personas,
            simulation_results=results,
            aggregated_insights=insights,
            is_public=exp_db.is_public or False,
            share_token=exp_db.share_token
        )
        
        return ExperimentResponse(
            experiment=experiment,
            status="completed",
            message="Simulation completed successfully"
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{experiment_id}/fork", response_model=ExperimentResponse)
async def fork_experiment(
    experiment_id: str, 
    new_feature: FeatureDescription,
    db: Session = Depends(get_db)
):
    """
    Fork an experiment to test a new feature with the same personas
    """
    original_exp = db.query(ExperimentDB).filter(ExperimentDB.id == experiment_id).first()
    
    if not original_exp:
        raise HTTPException(status_code=404, detail="Original experiment not found")
        
    try:
        # Create new ID
        new_id = str(uuid.uuid4())
        
        # Copy original data but with new feature
        new_exp = ExperimentDB(
            id=new_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            company_context=original_exp.company_context,
            personas=original_exp.personas, # Keep same personas
            feature_description=new_feature.model_dump_json(),
            simulation_results="[]", # Reset results
            aggregated_insights=None,
            is_public=False
        )
        
        db.add(new_exp)
        db.commit()
        db.refresh(new_exp)
        
        # Return new experiment response
        # Need to deserialize context and personas for response
        experiment = Experiment(
            id=new_id,
            created_at=new_exp.created_at,
            updated_at=new_exp.updated_at,
            company_context=_deserialize_model(new_exp.company_context, CompanyContext),
            feature_description=new_feature,
            personas=_deserialize_list(new_exp.personas, SyntheticPersona),
            simulation_results=[],
            aggregated_insights=None,
            is_public=False
        )
        
        return ExperimentResponse(
            experiment=experiment,
            status="forked",
            message="Experiment forked successfully. Ready for simulation."
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))