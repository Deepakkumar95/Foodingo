# src/utils/saga_manager.py
import asyncio
import logging
from typing import Dict, List, Callable, Any
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class SagaStatus(Enum):
    STARTED = "started"
    COMPENSATING = "compensating"
    COMPLETED = "completed"
    FAILED = "failed"

class SagaStep:
    def __init__(self, name: str, action: Callable, compensation: Callable):
        self.name = name
        self.action = action
        self.compensation = compensation
        self.completed = False
        self.compensated = False

class OrderSagaManager:
    def __init__(self):
        self.active_sagas: Dict[str, Dict] = {}
        self.saga_timeout = 300  # 5 minutes
        
    async def start_saga(self, saga_data: Dict = None) -> str:
        """Start a new saga and return saga ID"""
        saga_id = f"saga_{datetime.now().timestamp()}"
        
        self.active_sagas[saga_id] = {
            'id': saga_id,
            'status': SagaStatus.STARTED,
            'steps': [],
            'created_at': datetime.now(),
            'data': saga_data or {},
            'current_step': 0
        }
        
        logger.info(f"Saga {saga_id} started")
        return saga_id
    
    async def add_step(self, saga_id: str, step_name: str, 
                      action: Callable, compensation: Callable):
        """Add a step to the saga"""
        if saga_id not in self.active_sagas:
            raise ValueError(f"Saga {saga_id} not found")
        
        step = SagaStep(step_name, action, compensation)
        self.active_sagas[saga_id]['steps'].append(step)
        
        logger.debug(f"Step '{step_name}' added to saga {saga_id}")
    
    async def execute_saga(self, saga_id: str) -> bool:
        """Execute all steps in the saga"""
        if saga_id not in self.active_sagas:
            raise ValueError(f"Saga {saga_id} not found")
        
        saga = self.active_sagas[saga_id]
        steps = saga['steps']
        
        logger.info(f"Executing saga {saga_id} with {len(steps)} steps")
        
        for i, step in enumerate(steps):
            try:
                saga['current_step'] = i
                logger.info(f"Executing step {i+1}/{len(steps)}: {step.name}")
                
                # Execute step action
                if asyncio.iscoroutinefunction(step.action):
                    result = await step.action(saga['data'])
                else:
                    result = step.action(saga['data'])
                
                step.completed = True
                saga['data'][f'step_{i}_result'] = result
                
                logger.info(f"Step {step.name} completed successfully")
                
            except Exception as e:
                logger.error(f"Step {step.name} failed: {e}")
                await self.compensate_saga(saga_id, i)
                return False
        
        # All steps completed successfully
        saga['status'] = SagaStatus.COMPLETED
        logger.info(f"Saga {saga_id} completed successfully")
        return True
    
    async def compensate_saga(self, saga_id: str, failed_step_index: int):
        """Compensate saga from the failed step backwards"""
        if saga_id not in self.active_sagas:
            raise ValueError(f"Saga {saga_id} not found")
        
        saga = self.active_sagas[saga_id]
        saga['status'] = SagaStatus.COMPENSATING
        
        logger.warning(f"Compensating saga {saga_id} from step {failed_step_index}")
        
        # Compensate steps in reverse order
        steps = saga['steps']
        for i in range(failed_step_index - 1, -1, -1):
            step = steps[i]
            if step.completed and not step.compensated:
                try:
                    logger.info(f"Compensating step {i+1}: {step.name}")
                    
                    if asyncio.iscoroutinefunction(step.compensation):
                        await step.compensation(saga['data'])
                    else:
                        step.compensation(saga['data'])
                    
                    step.compensated = True
                    logger.info(f"Step {step.name} compensated successfully")
                    
                except Exception as e:
                    logger.error(f"Compensation failed for step {step.name}: {e}")
                    # Continue compensating other steps even if one fails
        
        saga['status'] = SagaStatus.FAILED
        logger.error(f"Saga {saga_id} failed and compensated")
    
    async def commit_saga(self, saga_id: str):
        """Commit saga (mark as completed successfully)"""
        if saga_id in self.active_sagas:
            saga = self.active_sagas[saga_id]
            saga['status'] = SagaStatus.COMPLETED
            logger.info(f"Saga {saga_id} committed")
    
    async def rollback_saga(self, saga_id: str):
        """Rollback saga (compensate all steps)"""
        if saga_id in self.active_sagas:
            saga = self.active_sagas[saga_id]
            steps_completed = sum(1 for step in saga['steps'] if step.completed)
            
            if steps_completed > 0:
                await self.compensate_saga(saga_id, steps_completed)
            else:
                saga['status'] = SagaStatus.FAILED
                logger.info(f"Saga {saga_id} rolled back (no steps executed)")
    
    async def get_saga_status(self, saga_id: str) -> Dict:
        """Get saga status and details"""
        if saga_id not in self.active_sagas:
            raise ValueError(f"Saga {saga_id} not found")
        
        saga = self.active_sagas[saga_id]
        
        return {
            'id': saga_id,
            'status': saga['status'].value,
            'created_at': saga['created_at'].isoformat(),
            'current_step': saga['current_step'],
            'total_steps': len(saga['steps']),
            'steps_completed': sum(1 for step in saga['steps'] if step.completed),
            'steps_compensated': sum(1 for step in saga['steps'] if step.compensated)
        }
    
    async def cleanup_old_sagas(self):
        """Clean up old completed/failed sagas"""
        current_time = datetime.now()
        sagas_to_remove = []
        
        for saga_id, saga in self.active_sagas.items():
            saga_age = (current_time - saga['created_at']).total_seconds()
            
            if (saga['status'] in [SagaStatus.COMPLETED, SagaStatus.FAILED] and 
                saga_age > self.saga_timeout):
                sagas_to_remove.append(saga_id)
        
        for saga_id in sagas_to_remove:
            del self.active_sagas[saga_id]
            logger.debug(f"Cleaned up old saga: {saga_id}")
        
        if sagas_to_remove:
            logger.info(f"Cleaned up {len(sagas_to_remove)} old sagas")
    
    def get_active_sagas_count(self) -> int:
        """Get count of active sagas"""
        return len(self.active_sagas)
