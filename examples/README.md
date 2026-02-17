# Example Configuration Files

This directory contains example configuration files for different scenarios.

## Files

- `production-config.yml` - Production environment template
- `development-config.yml` - Development environment template
- `rac-config.yml` - RAC configuration example
- `dataguard-config.yml` - Data Guard configuration example

## Usage

```bash
# Copy and customize
cp examples/production-config.yml my-prod-config.yml
nano my-prod-config.yml

# Use with oradba
oradba install --config my-prod-config.yml --full
```

## Important

⚠️ **ALWAYS change default passwords before using in production!**
