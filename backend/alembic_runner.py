import sys
from alembic.config import main

if __name__ == '__main__':
    sys.argv = ['alembic', 'upgrade', 'head']
    try:
        sys.exit(main())
    except Exception as e:
        print("ALEMBIC ERROR:", e)
