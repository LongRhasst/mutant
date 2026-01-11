import asyncio
import httpx
import os
from datetime import datetime, timezone


async def run_model_service(SMILES: list[str]):
    """
    Service to trigger and monitor Airflow DAG execution
    """
    airflow_url = os.getenv("AIRFLOW_URL")
    dag_id = "molecule_mutation_pipeline"
    username = os.getenv("AIRFLOW_USERNAME")
    password = os.getenv("AIRFLOW_PASSWORD")
    
    async with httpx.AsyncClient(timeout=300.0) as client:
        try:

            url = f"{airflow_url}/api/v1/dags/{dag_id}/dagRuns"
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")[:-3]
            dag_run_id = f"manual__{timestamp}"
                        
            response = await client.post(
                url,
                auth=(username, password),
                headers={"Content-Type": "application/json"},
                json={
                    "dag_run_id": dag_run_id,
                    "logical_date": datetime.now(timezone.utc).isoformat(),
                    "conf": {"smiles": SMILES, "max_mutants": 50}
                }
            )
            
            if response.status_code not in [200, 201]:
                return {
                    "total_inputs": len(SMILES),
                    "status": "failed",
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "completed": False
                }
            
            status_url = f"{airflow_url}/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}"
            max_wait_time = 300
            elapsed_time = 0
            
            while elapsed_time < max_wait_time:
                await asyncio.sleep(5)
                elapsed_time += 5
                
                status_response = await client.get(status_url, auth=(username, password))
                if status_response.status_code == 200:
                    dag_status = status_response.json().get("state")
                    if dag_status in ["success", "failed"]:
                        return {
                            "total_inputs": len(SMILES),
                            "dag_run_id": dag_run_id,
                            "status": dag_status,
                            "completed": True
                        }
            
            return {
                "total_inputs": len(SMILES),
                "dag_run_id": dag_run_id,
                "status": "timeout",
                "error": "DAG execution timeout",
                "completed": False
            }
            
        except Exception as e:
            error_message = f"Status: failed, Total inputs: {len(SMILES)}, Error: {str(e)}"
            raise Exception(error_message) from e
