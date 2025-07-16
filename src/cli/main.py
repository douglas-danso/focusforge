import click
from src.agents.llm_decomposer import decompose_task

@click.group()
def cli():
    pass

@click.command()
@click.argument("task")
@click.option("--duration", default=60, help="Estimated duration in minutes.")
def add(task, duration):
    blocks = decompose_task(task, duration)
    click.echo("\n📋 Task Breakdown:")
    for block in blocks:
        click.echo(f" - {block.strip()}")

cli.add_command(add)

if __name__ == "__main__":
    cli()
