import sys
from gridguard.pipeline import main
if __name__ == '__main__':
    sys.argv.extend(['--action','evaluate'])
    main()
