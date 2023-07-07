#!/usr/bin/env python
import datetime
import json
import click
from typing import Union
from rich.console import Console
from requests.models import Response

from api_client import ApiRunner
from tables import FarmsTable, FarmFieldsTable, WorkerFarmsTable, WorkerTasksTable, WorkerAssignmentsTable, WorkOrdersTable, EmptyResponseTable


runner = ApiRunner('http://127.0.0.1:8000')
console = Console()


@click.group()
def cli_commands():
    pass


from commands.farms import *
from commands.fields import *
# from commands.backend import *


@cli_commands.command()
def fields_by_farm() -> None:
    response = runner.call('/farms', 'GET', 400, 'could not retrieve farms')    
    FarmsTable(response.json(), print=True)
    
    chosen_farm_id = input('Select a farm ID: ')
    print('')
    if len([item for item in response.json() if item['id'] == int(chosen_farm_id)]) > 0: # type: ignore
        response = runner.call(f'/farms/{chosen_farm_id}/fields', 'GET', 400, 'could not retrive fields for farm')          
        FarmFieldsTable(response.json(), print=True)


@cli_commands.command()
@click.option('--name', '-n', type=str, prompt='Name')
@click.option('--role', '-r', type=click.Choice(['transport', 'auger', 'operator', 'production']), prompt='Role')
def create_worker(name: str, role: str) -> None:
    action = 'create'
    worker_id = None

    response = runner.call(f'/workers/name/{name}', 'GET', 400, 'could not locate a worker with that name')   
    if len([(k,v) for k, v in response.json().items() if v == name]) > 0: # type: ignore
        action = 'associate'
    worker_id = response.json()['id'] # type: ignore
    

    response = runner.call('/farms', 'GET', 400, 'could not retrieve farms')    
    FarmsTable(response.json(), print=True)

    chosen_farm_id = input('Select a farm ID: ')
    print('')
    
    if len([item for item in response.json() if item['id'] == int(chosen_farm_id)]) > 0: # type: ignore
        if action == 'create':
            payload = {
                'name': name,
                'role': role,
            }

            submitted_changes = {key:value for (key,value) in payload.items() if value is not None}
            
            response = runner.call(f'/workers', 'POST', 500, 'could not create worker', submitted_changes)
            worker = response.json()
            runner.call(f'/workers/{worker["id"]}/farm/{chosen_farm_id}/associate', 'POST', 500, 'failed to associate worker with farm')
            
            response = runner.call(f'/workers/{worker["id"]}', 'GET', 400, 'could not retrieve worker')
            WorkerFarmsTable(response.json(), print=True)
        else:
            runner.call(f'/workers/{worker_id}/farm/{chosen_farm_id}/associate', 'POST', 500, 'failed to associate worker with farm')


@cli_commands.command()
def assign_worker_to_farm(worker_id: int, farm_id: int):
    response = runner.call(f'/workers/{worker_id}/farm/{farm_id}/associate', 'POST', 500, 'unable to assign worker to farm')


@cli_commands.command()
def create_work_order():
    response = runner.call('/workers', 'GET', 400, 'unable to fetch workers')
    WorkerFarmsTable(response.json(), print=True)
    
    chosen_worker_id = input('Select a worker ID: ')
    print('')

    if len([item for item in response.json() if item['id'] == int(chosen_worker_id)]) > 0: # type: ignore
        response = runner.call('/farms', 'GET', 400, 'unable to fetch farms')
        FarmsTable(response.json(), print=True)

        chosen_farm_id = input('Select a farm ID: ')
        print('')

        response = runner.call(f'/farms/{chosen_farm_id}/fields', 'GET', 400, 'unable to fetch farms')
        FarmsTable(response.json(), print=True)

        chosen_field_id = input('Select a field ID: ')
        print('')

        response = runner.call(f'/orders/tasks', 'GET', 400, 'unable to fetch work order tasks')
        WorkerTasksTable(response.json(), print=True)
        
        chosen_task_ids = input('Add tasks in order of preference (comma-delimited): ')


        response = runner.call(f'/orders', 'POST', 500, 'unable to create work order', payload={
            'created': datetime.datetime.now().strftime('%Y-%m-%d'),
            'farm_id': chosen_farm_id,
            'field_id': chosen_field_id,
            'worker_id': chosen_worker_id,
            'tasks': chosen_task_ids,
        })

        work_order = json.loads(response.content) # type: ignore
        runner.call(f'/orders/{work_order["id"]}/generate', 'POST', 500, 'error generating order assignments')
        runner.call(f'/orders/{work_order["id"]}/plan', 'PUT', 500, 'error creating order plan')


@cli_commands.command()
@click.option('--prop', '-p', type=click.Choice(['completed', 'task_name', 'worker_id', 'farm_id', 'field_id', 'work_order_id', 'due']))
@click.option('--value', '-v', type=str)
@click.option('--hide-completed', '-hc', is_flag=True, default=False)
def get_assignments(prop: str, value: str, hide_completed: bool):
    response = runner.call(f'/assignments/filter', 'POST', 500, 'unable to fetch assignments', [{
        'property': prop,
        'value': value,
        'hide_completed': hide_completed,
    }])

    WorkerAssignmentsTable(response.json(), print=True)


@cli_commands.command()
@click.option('--assignment-id', '-a', type=int)
def complete_assignment(assignment_id: int):
    resp_tasks = runner.call('/orders/tasks', 'GET', 400, 'unable to fetch tasks')
    resp_assignment = runner.call(f'/assignments/{assignment_id}', 'GET', 400, 'failed to locate assignment')
    response_obj = resp_assignment.json()
    payload = {}
    if response_obj['task_id'] in [task['id'] for task in resp_tasks.json() if task['name'] in ['forage', 'harvest']]:
        assignment_yield = input('Enter the crop yield: ')    
        resp_order = runner.call(f'/orders/{1}', 'GET', 400, 'failed to locate work order')        
        resp_obj_order = resp_order.json()
        field_id = resp_obj_order['field']['id']
        payload = {
            'field_id': field_id,
            'assignment_id': assignment_id,
            'amount_yield': assignment_yield
        }
        runner.call(f'/fields/{field_id}/yield', 'POST', 500, 'Field not found', payload=payload)
    runner.call(f'/assignments/{assignment_id}/complete', 'PUT', 500, 'Error completing assignment')


@cli_commands.command()
def get_orders():
    response = runner.call(f'/orders', 'GET', 500, 'failed to mark assignment completed')
    WorkOrdersTable(response.json(), print=True)


@cli_commands.command()
@click.option('--provision', '-p', is_flag=True, default=False)
@click.option('--calendars', '-c', type=click.Path(exists=True, readable=True), default=None)
@click.option('--worktasks', '-w', type=click.Path(exists=True, readable=True), default=None)
def bootstrap(provision: bool, calendars=None, worktasks=None):
    contents = ''

    if provision:
        runner.call('/backend/provision', 'POST', 500, 'unable to provision database')
    
    if calendars:
        with open(calendars, 'r') as fh:
            contents = json.loads(fh.read())
        runner.call('/backend/calendars', 'POST', 500, 'unable to bootstrap crop calendars', payload=contents)
    if worktasks:
        with open(worktasks, 'r') as fh:
            contents = json.loads(fh.read())
        runner.call('/backend/worktasks', 'POST', 500, 'unable to bootstrap work tasks', payload=contents)


if __name__ == '__main__':
    entry = click.CommandCollection(sources=[cli_commands, entry_fields, entry_farms])
    entry()
