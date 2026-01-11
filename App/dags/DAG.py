from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import asyncio
import psycopg2
from psycopg2.extras import execute_batch
import os
import redis.asyncio as redis

sys.path.insert(0, '/opt/airflow')

from Services import generate_mutants, calculate_properties

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

def redis_connect():
    return redis.from_url("redis://redis:6379")

def get_dag_params(**context) -> None:
    dag_conf = context['dag_run'].conf or {}
    input_smiles = dag_conf.get('smiles')
    max_mutants = dag_conf.get('max_mutants', 50)

    if not input_smiles:
        print("No input SMILES provided")
        return {"mutants": []}
    
    async def process_all():
        r_client = redis_connect()
        redis_keys = []
        semaphore = asyncio.Semaphore(100)
        
        async def process_smiles(smi):
            async with semaphore:
                try:
                    mutant_data = await generate_mutants(smi, max_mutants)
                    mutants_list = mutant_data.get('mutants', [])
                    
                    smi_key = f"mutants:{smi}"
                    await r_client.set(smi_key, str(mutants_list))
                    return smi_key
                except Exception as e:
                    print(f"Error processing {smi}: {e}")
                    return None
        
        tasks = [process_smiles(smi) for smi in input_smiles]
        results = await asyncio.gather(*tasks)
        redis_keys = [key for key in results if key is not None]
        
        await r_client.close()
        return redis_keys
    
    results = asyncio.run(process_all())
    
    ti = context['task_instance']
    ti.xcom_push(key='redis_keys', value=results)
    
    return {'redis_keys': results, 'mutants_count': len(results)}

def calculate_props_wrapper(**context):
    
    async def process_properties():
        r_client = redis_connect()
        ti = context['task_instance']
        redis_keys = ti.xcom_pull(task_ids='generate_mutants', key='redis_keys')
        
        if not redis_keys:
            print("No Redis keys found in XCom")
            return []
        
        print(f"Calculating properties for mutants from {len(redis_keys)} Redis keys")
        
        semaphore = asyncio.Semaphore(100)
        
        async def calculate(smi):
            async with semaphore:
                try:
                    props = await calculate_properties(smi)
                    return props
                except Exception as e:
                    print(f"Error calculating properties for {smi}: {e}")
                    return None
        
        all_tasks = []
        for key in redis_keys:
            mutants_data = await r_client.get(key)
            if mutants_data:
                import ast
                try:
                    mutants_list = ast.literal_eval(mutants_data.decode('utf-8'))
                except:
                    mutants_list = eval(mutants_data.decode('utf-8'))
                
                all_tasks.extend([calculate(smi) for smi in mutants_list])
        
        props_results = await asyncio.gather(*all_tasks)
        results = [props for props in props_results if props is not None]
        
        await r_client.close()
        return results
    
    results = asyncio.run(process_properties())
    print(f"Calculated properties for {len(results)} mutants")
    return results

def save_to_postgres(**context):
    ti = context['task_instance']
    results = ti.xcom_pull(task_ids='calculate_properties')
    
    session_name = datetime.now().strftime("session_%Y%m%d_%H%M%S")
    
    if not results:
        print("No valid results to save")
        return {"saved": 0, "status": "no_data"}
    
    sorted_results = sorted(results, key=lambda x: x.get('score', 0), reverse=True)
    print(f"Sorted {len(sorted_results)} mutants by score")
    
    db_url = "postgresql://airflow:airflow@postgres:5432/airflow"
    
    try:
        conn = psycopg2.connect(
            db_url
        )
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS molecule_mutants (
                id SERIAL PRIMARY KEY,
                mutant_smiles TEXT NOT NULL,
                score FLOAT NOT NULL,
                rank INTEGER NOT NULL,
                session_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        insert_data = [
            (result['smiles'], result['score'], rank + 1, session_name)
            for rank, result in enumerate(sorted_results)
        ]
        
        chunk_size = 1000
        for i in range(0, len(insert_data), chunk_size):
            chunk = insert_data[i:i + chunk_size]
            execute_batch(
                cursor,
                """
                INSERT INTO molecule_mutants (mutant_smiles, score, rank, session_name)
                VALUES (%s, %s, %s, %s)
                """,
                chunk,
                page_size=100
            )
        
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return {"saved": len(insert_data), "status": "success", "top_score": sorted_results[0]['score'] if sorted_results else None}
        
    except Exception as e:
        print(f"Error saving to PostgreSQL: {str(e)}")
        return {"saved": 0, "status": "error", "error": str(e)}

with DAG(
    dag_id = 'molecule_mutation_pipeline',
    default_args=default_args,
    description='A DAG to generate molecular mutants using defined mutation rules',
    schedule=None,
    catchup=False,
) as dag:

    t1 = PythonOperator(
        task_id = 'generate_mutants',
        python_callable = get_dag_params,
    )

    t2 = PythonOperator(
        task_id = 'calculate_properties',
        python_callable = calculate_props_wrapper,
    )

    t3 = PythonOperator(
        task_id = 'save_to_postgres',
        python_callable = save_to_postgres,
    )

    t1 >> t2 >> t3