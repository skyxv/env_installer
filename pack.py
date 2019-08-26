import os
import sys

from src.env_installer import env_installer


if __name__ == '__main__':
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    env_installer.pack()

