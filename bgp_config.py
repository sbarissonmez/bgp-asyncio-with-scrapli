import os
import asyncio
import yaml
from jinja2 import Environment, FileSystemLoader
from scrapli.driver.core import AsyncIOSXEDriver
from rich import print as rprint
from inventory import DEVICES

username = os.environ["USERNAME"]
password = os.environ["PASSWORD"]


def generate_config(device):
    """
    This line of code loads YAML configuration data for each device in a list from the corresponding host variables file.
    Render configuration using the jinja2 template engine.
    """
    hostname = device["hostname"]
    config_data = yaml.safe_load(open(f"host_vars/{hostname}.yaml"))
    env = Environment(
        loader=FileSystemLoader("./templates"), trim_blocks=True, lstrip_blocks=True
    )
    template = env.get_template("bgp.j2")
    configuration = template.render(config_data)
    return configuration


async def push_config(device):
    """
    This refers to a coroutine that establishes a connection and sends configuration to a device.
    """
    async with AsyncIOSXEDriver(
        host=device["host"],
        auth_username=username,
        auth_password=password,
        auth_strict_key=False,
        transport="asyncssh",
    ) as conn:
        prompt_result = await conn.get_prompt()
        cfg = generate_config(device).splitlines()
        configs_result = await conn.send_configs(configs=cfg)
    return prompt_result, configs_result


async def main():
    """
    The primary coroutine.
    """
    coroutines = [push_config(device) for device in DEVICES]
    results = await asyncio.gather(*coroutines)
    for result in results:
        rprint(f"[green]{result[0]}[/green]")
        rprint(f"{result[1].result}\n\n")


asyncio.run(main())
