import os
import sys
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.env_installer import env_installer
from src.exceptions import MissingParamError


class EnvInstallerTest(unittest.TestCase):

    def test_get_download_folder_name(self):
        self.assertRegex(env_installer._get_download_folder_name(), "[abcdef0123456789]{16}")

    def test_validate(self):
        self.assertRaises(FileNotFoundError, env_installer._validate_base_dir, "/abcdefg")
        self.assertRaises(FileNotFoundError, env_installer._validate_req_dir, "/abcdefg")

    def test_get_single_pack_cmd(self):
        self.assertEqual(env_installer._get_single_pack_cmd("/a", "pkg", "www.com"), "pip download -d /a -i www.com pkg")
        self.assertEqual(env_installer._get_single_pack_cmd("/a", "pkg"), "pip download -d /a pkg")
        self.assertRaises(MissingParamError, env_installer._get_single_pack_cmd, "/a", "")

    def test_get_pack_cmd(self):
        self.assertEqual(env_installer._get_pack_cmd("/a", "/r", "www.com", need_venv=True),
                         "pip download -d /a -r /r -i www.com && pip download -d /a -i www.com virtualenv")
        self.assertEqual(env_installer._get_pack_cmd(download_dir="/a", req_dir="/r", need_venv=False), "pip download -d /a -r /r")

    def test_re_pattern(self):
        self.assertRegex('virtualenv-16.whl', env_installer._venv_pkg_pattern)
        self.assertNotRegex('virtualenv.whl', env_installer._venv_pkg_pattern)

    def test_search_file(self):
        self.assertEqual(env_installer._search_file("/usr", env_installer._venv_pkg_pattern), None)

    def test_get_install_cmd(self):
        self.assertEqual(env_installer._get_install_cmd("/a", "/r", "virutalenv", "/pip"),
                         "sudo /pip install -r /r --no-index --find-links=/a")
        self.assertEqual(env_installer._get_install_cmd("/a", pkg_name="virtualenv"),
                         "pip3 install virtualenv --no-index --find-links=/a")
        self.assertRaises(MissingParamError, env_installer._get_install_cmd, "/a")

    def test_get_venv_name(self):
        self.assertEqual(len(env_installer._get_venv_name()), 13)

    def test_make_executable_cmd(self):
        venv_path = "~/test_env"
        self.assertEqual(env_installer._make_executable_cmd(venv_path),
                         "chmod +x ~/test_env/bin/activate")

    def test_validate_py_path(self):
        file_path = "~/test_file"
        try:
            os.makedirs(file_path)
        except FileExistsError:
            pass
        self.assertEqual(env_installer._validate_py_path(file_path), file_path)
        env_installer._rm_folder(file_path)

    def test_make_virtualenv_cmd(self):
        self.assertEqual(env_installer._make_virtualenv_cmd("/usr/bin/python3", "venv"),
                         "virtualenv -p /usr/bin/python3 venv")


if __name__ == '__main__':
    unittest.main()
