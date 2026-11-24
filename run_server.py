"""Dedicated single-process host entry point. No provider resources are created."""
import os
import uvicorn


def resolve_port(value):
    if not value.isascii() or not value.isdigit() or not 1 <= int(value) <= 65535:
        raise ValueError('PORT must be an integer from 1 to 65535')
    return int(value)


if __name__ == '__main__':
    uvicorn.run('api.main:app', host='0.0.0.0', port=resolve_port(os.environ.get('PORT', '4182')), workers=1)
