from typing import Union
from rich.table import Table
from rich.console import Console
from tzlocal import get_localzone
from delorean import Delorean, parse


class RichTable():
    table = None
    data = []
    print = False
    console = Console()

    def __init__(self, data, header_style: str, print: bool):
        self.data = [data] if type(data) != list else data
        self.table = Table(show_header=True, header_style=header_style)
        self.print = print


class EmptyResponseTable(RichTable):
    def __init__(self, data, header_style: str = 'bold white', print: bool = False):
        super().__init__(data, header_style, print)

        if self.table:
            self.table.add_column('Response')
            self.add_rows()
            if self.print:
                self.console.print(self.table)
    

    def add_rows(self):
        if self.table:
            for item in self.data:
                self.table.add_row(item['message'])


class FarmFieldsTable(RichTable):
    def __init__(self, data, header_style: str = 'bold white', print: bool = False):
        super().__init__(data, header_style, print)

        if self.table:
            self.table.add_column('Farm', style='dim')
            self.table.add_column('Id', style='dim')
            self.table.add_column('Name')
            self.table.add_column('Acreage', justify='right')
            self.table.add_column('Crop')
            self.table.add_column('Yield Potential %', justify='right')
            self.table.add_column('Action')
            self.table.add_column('Notes')
            self.add_rows()
            if self.print:
                self.console.print(self.table)


    def add_rows(self):
        if self.table:
            for item in self.data:
                    self.table.add_row(
                        f'[bold]{item["farm"]["name"]}[/bold]',
                        str(item['id']),
                        f'[bold]{item["name"]}[/bold]',
                        str(item['acreage']),
                        item['crop'],
                        str(item['yield_potential']),
                        item['action'],
                        item["notes"],
                    )


class FarmFieldsTableTest(RichTable):
    def __init__(self, data, header_style: str = 'bold white', print: bool = False):
        super().__init__(data, header_style, print)

        if self.table:
            self.table.add_column('Farm', style='dim')
            self.table.add_column('Id', style='dim')
            self.table.add_column('Name')
            self.table.add_column('Acreage', justify='right')
            self.table.add_column('Crop')
            self.table.add_column('Yield Potential %', justify='right')
            self.table.add_column('Action')
            self.table.add_column('Notes')
            self.add_rows()
            if self.print:
                self.console.print(self.table)


    def add_rows(self):
        if self.table:
            for item in self.data:
                self.table.add_row(
                    f'[bold]{item["farm"]["name"]}[/bold]',
                    str(item['id']),
                    f'[bold]{item["name"]}[/bold]',
                    str(item['acreage']),
                    item['crop'],
                    str(item['yield_potential']),
                    item['action'],
                    item["notes"],
                )


class FarmsTable(RichTable):
    def __init__(self, data, header_style: str = 'bold white', print: bool = False):
        super().__init__(data, header_style, print)
        if self.table:
            self.table.add_column('Id', style='dim')
            self.table.add_column('Name')
            self.add_rows()
            if self.print:
                self.console.print(self.table)
    

    def add_rows(self):
        if self.table:
            for item in self.data:
                self.table.add_row(
                    str(item['id']),
                    f'[bold]{item["name"]}[/bold]',
                )


class WorkerFarmsTable(RichTable):
    def __init__(self, data, header_style: str = 'bold white', print: bool = False):
        super().__init__(data, header_style, print)

        if self.table:
            self.table.add_column('Id', style='dim')
            self.table.add_column('Name')
            self.table.add_column('Role')
            self.add_rows()
            if self.print:
                self.console.print(self.table)
    
    def add_rows(self):
        if self.table:
            for item in self.data:
                self.table.add_row(
                    str(item['id']),
                    f'[bold]{item["name"]}[/bold]',
                    str(item['role']),
                )


class WorkerTasksTable(RichTable):
    def __init__(self, data, header_style: str = 'bold white', print: bool = False):
        super().__init__(data, header_style, print)

        if self.table:
            self.table.add_column('Id', style='dim')
            self.table.add_column('Name')
            self.table.add_column('Category', style='dim')
            self.add_rows()
            if self.print:
                self.console.print(self.table)
    
    def add_rows(self):
        if self.table:
            for item in self.data:
                self.table.add_row(
                    str(item['id']),
                    item['name'],
                    item['category']
                )


class WorkOrdersTable(RichTable):
    def __init__(self, data, header_style: str = 'bold white', print: bool = False):
        super().__init__(data, header_style, print)

        if self.table:
            self.table.add_column('#')
            self.table.add_column('Created')
            self.table.add_column('Farm')
            self.table.add_column('Field')
            self.table.add_column('Worker')
            self.table.add_column('Tasks')
            self.table.add_column('Completed')
            self.add_rows()
            if self.print:
                self.console.print(self.table)
    
    def add_rows(self):
        if self.table:
            for item in self.data:                 
                d = parse(item['created'], get_localzone().key) # type: ignore
                d_completed = parse(item['completed'], get_localzone().key) if item['completed'] else None # type: ignore
                d_completed = f'[bold green]{d_completed.datetime.strftime("%Y-%m-%d")}[/bold green]' if d_completed else '[bold]False[/bold]'
                self.table.add_row(
                    str(item['id']),
                    d.datetime.strftime("%Y-%m-%d"),
                    str(item['farm']['name']),
                    str(item['field']['name']),
                    str(item['worker']['name']),
                    item['tasks'],
                    f'[bold]{d_completed}[/bold]',
                )


class WorkerAssignmentsTable(RichTable):
    def __init__(self, data, header_style: str = 'bold white', print: bool = False):
        super().__init__(data, header_style, print)
    
        if self.table:
            self.table.add_column('#')
            self.table.add_column('Started On', style='dim')
            self.table.add_column('Worker')
            self.table.add_column('Role')
            self.table.add_column('Farm')
            self.table.add_column('Field')
            self.table.add_column('Task')
            self.table.add_column('Due')
            self.table.add_column('Completed')
            self.add_rows()
            if self.print:
                self.console.print(self.table)
    

    def expand_month(self, month_number: int) -> str:
        months = {
            1: 'Jan',
            2: 'Feb',
            3: 'Mar',
            4: 'Apr',
            5: 'May',
            6: 'Jun',
            7: 'Jul',
            8: 'Aug',
            9: 'Sep',
            10: 'Oct',
            11: 'Nov',
            12: 'Dec',
        }
        
        return months[month_number]


    def add_rows(self):
        if self.table:
            for item in self.data:
                d = parse(item['started'], get_localzone().key) # type: ignore
                if item['month_assigned'] > 12:
                    from pprint import pprint
                    import ipdb; ipdb.set_trace()
                    x = None
                    
                self.table.add_row(
                    str(item['assignment_id']),
                    d.datetime.strftime("%Y-%m-%d %H:%M"),
                    item['worker_name'],
                    item['worker_role'],
                    item['farm_name'],
                    item['field_name'],
                    item['task_name'],
                    self.expand_month(item['month_assigned']),
                    '[bold green]Yes[/bold green]' if item['completed'] == True else '[bold]No[/bold]',
                )
