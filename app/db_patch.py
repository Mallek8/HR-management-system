"""
UTF-8 encoding setup for psycopg2 on Windows.

This module MUST be imported BEFORE any psycopg2 import to ensure
proper UTF-8 encoding configuration.

The issue: psycopg2's C extension may read system paths or environment
variables containing non-UTF-8 bytes (e.g., 'é' as 0xe9 in latin-1),
causing UnicodeDecodeError when psycopg2 tries to decode them as UTF-8.

Solution: Set PGCLIENTENCODING=UTF8 before psycopg2 is imported,
ensuring all environment variables are UTF-8 safe.
"""
import os
import sys

# Set UTF-8 encoding for PostgreSQL client BEFORE psycopg2 is imported
if sys.platform == 'win32':
    # Remove any existing PostgreSQL environment variables that might interfere
    pg_vars_to_remove = [k for k in list(os.environ.keys()) 
                        if k.upper().startswith('PG') and k != 'PGCLIENTENCODING']
    for key in pg_vars_to_remove:
        try:
            del os.environ[key]
        except KeyError:
            pass
    
    # Explicitly set UTF-8 encoding for PostgreSQL client
    os.environ['PGCLIENTENCODING'] = 'UTF8'
    
    # Ensure Python uses UTF-8 for file I/O
    if hasattr(sys, 'setdefaultencoding'):
        # Python 2 compatibility (not needed in Python 3, but harmless)
        sys.setdefaultencoding('utf-8')
