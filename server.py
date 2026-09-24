import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("iac-mcp-server")

MODULES = {
    "azure-storage-account": {
        "description": "Secure Azure Storage Account Terraform module.",
        "source": "git::https://github.com/aldo2510/terraform-modules.git//modules/azure-storage-account?ref=main",
        "required": ["name", "resource_group_name", "location", "environment"],
        "optional": {
            "account_replication_type": "LRS",
            "public_network_access_enabled": False,
            "tags": {}
        }
    }
}

@mcp.tool()
def list_modules() -> str:
    """List approved Terraform modules."""
    return json.dumps([
        {"name": name, "description": data["description"]}
        for name, data in MODULES.items()
    ], indent=2)

@mcp.tool()
def get_module(name: str) -> str:
    """Return metadata and required inputs for an approved module."""
    if name not in MODULES:
        return json.dumps({"error": f"Unknown module: {name}"})
    return json.dumps({"name": name, **MODULES[name]}, indent=2)

@mcp.tool()
def validate_parameters(module: str, parameters: dict) -> str:
    """Validate that required module parameters are present."""
    if module not in MODULES:
        return json.dumps({"valid": False, "errors": [f"Unknown module: {module}"]})
    required = MODULES[module]["required"]
    missing = [key for key in required if not parameters.get(key)]
    return json.dumps({
        "valid": not missing,
        "missing": missing,
        "parameters": parameters
    }, indent=2)

@mcp.tool()
def generate_terraform(module: str, parameters: dict) -> str:
    """Generate a Terraform root module using an approved module."""
    validation = json.loads(validate_parameters(module, parameters))
    if not validation["valid"]:
        return json.dumps(validation, indent=2)

    source = MODULES[module]["source"]
    lines = [
        'terraform {',
        '  required_version = ">= 1.5.0"',
        '',
        '  required_providers {',
        '    azurerm = {',
        '      source  = "hashicorp/azurerm"',
        '      version = "~> 4.0"',
        '    }',
        '  }',
        '}',
        '',
        'provider "azurerm" {',
        '  features {}',
        '}',
        '',
        f'module "{module}" {{',
        f'  source = "{source}"',
        ''
    ]

    for key, value in parameters.items():
        if isinstance(value, bool):
            rendered = "true" if value else "false"
        elif isinstance(value, dict):
            rendered = json.dumps(value)
        else:
            rendered = json.dumps(value)
        lines.append(f"  {key} = {rendered}")

    lines += ['}', '']
    return "\n".join(lines)

if __name__ == "__main__":
    mcp.run()
