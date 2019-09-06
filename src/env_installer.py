import os
import re
import random
import shutil
import argparse

from src.exceptions import UnreadableError, MissingParamError, InvalidInterpreterPathError
from src.utils import ColorfulOutput as output


class EnvInstaller:
    """
    Project dependent packaging and installation.
    """
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Env Installer:Install the python project "
                                                          "environment offline easily and gracefully.")
        self._envlib_file_name = ".envlib"

    @staticmethod
    def _get_download_folder_name(s="abcdef0123456789", length=16):
        return ''.join(random.sample(s, length))

    @staticmethod
    def _is_exist_path(path):
        return os.path.exists(path)

    @staticmethod
    def _is_readable(file_path):
        return os.access(file_path, os.R_OK)

    @staticmethod
    def _is_executable(file_path):
        return os.access(file_path, os.X_OK)

    @staticmethod
    def _is_dir(path):
        return os.path.isdir(path)

    def _add_pack_args(self):
        self.parser.add_argument("-b", "--base-dir",
                                 help="absolute path of the project to be packaged.",
                                 action="store", required=True)
        self.parser.add_argument("-r", "--req-dir",
                                 help="absolute path of production environment dependency file.",
                                 action="store", required=True)
        self.parser.add_argument("-d", "--download_dir",
                                 help="optional, absolute path of package storage location."
                                      "if not given, it is automatically generated under the project",
                                 action="store", default=self._get_download_folder_name())
        flag_parser = self.parser.add_mutually_exclusive_group(required=False)
        flag_parser.add_argument('-v', dest='v', action='store_true',
                                 help="if need to download an additional `virtualenv` package, "
                                      "use this param. default false.")
        self.parser.set_defaults(v=False)
        self.parser.add_argument("-i", "--index-url",
                                 help="download package index url, equivalent to `pip install -i`.",
                                 action="store")
        return self.parser.parse_args()

    def _add_install_args(self):
        self.parser.add_argument("-b", "--base-dir",
                                 help="absolute path of the project to be deployed.",
                                 action="store", required=True)
        self.parser.add_argument("-r", "--req-dir",
                                 help="absolute path of production environment dependency file.",
                                 action="store", required=True)
        self.parser.add_argument("--venv-pip-path",
                                 help="the pip absolute path of the virtual environment that already exists on the server.",
                                 action="store")
        self.parser.add_argument("-p", "--python",
                                 help="python interpreter path on the server.equivalent to `virtualenv -p`.",
                                 action="store")
        return self.parser.parse_args()

    def _validate_base_dir(self, base_dir):
        if not self._is_exist_path(base_dir):
            raise FileNotFoundError("the specified base directory does not exist.")
        return base_dir

    def _validate_req_dir(self, req_dir):
        if not self._is_exist_path(req_dir):
            raise FileNotFoundError("the specified dependency file does not exist.")
        if not self._is_readable(req_dir):
            raise UnreadableError("the specified dependency file is unreadable.")
        return req_dir

    @staticmethod
    def _rm_folder(folder_path):
        shutil.rmtree(folder_path)

    def _create_download_dir(self, base_dir, download_dir):
        download_dir_file = base_dir + "/" + self._envlib_file_name
        os.chdir(base_dir)
        os.makedirs(download_dir)
        with open(download_dir_file, 'w') as f:
            f.write(download_dir)

    def _fetch_download_dir(self, base_dir):
        with open(base_dir + "/" + self._envlib_file_name, 'r') as f:
            download_dir = f.read()
        return download_dir

    def _rm_download_dir(self, base_dir, absolute_download_dir):
        self._rm_folder(absolute_download_dir)
        download_dir_file = base_dir + "/" + self._envlib_file_name
        if os.path.exists(download_dir_file):
            os.remove(download_dir_file)

    def _validate_download_dir(self, base_dir, download_dir):
        absolute_download_dir = base_dir + "/" + download_dir
        if not self._is_exist_path(absolute_download_dir):
            self._create_download_dir(base_dir, download_dir)
            return absolute_download_dir
        else:
            raise FileExistsError("Cannot use an existing directory as a download dir: {}".format(
                absolute_download_dir))

    @staticmethod
    def _get_single_pack_cmd(download_dir, pkg_name, index_url=None):
        if pkg_name:
            if index_url:
                return "pip download -d {} -i {} {}".format(download_dir, index_url, pkg_name)
            else:
                return "pip download -d {} {}".format(download_dir, pkg_name)
        else:
            raise MissingParamError("`pkg_name` can not be `None`.")

    def _get_pack_cmd(self, download_dir, req_dir, index_url=None, need_venv=False):
        if index_url:
            req_cmd = "pip download -d {} -r {} -i {}".format(download_dir, req_dir, index_url)
        else:
            req_cmd = "pip download -d {} -r {}".format(download_dir, req_dir)
        if need_venv:
            venv_cmd = self._get_single_pack_cmd(download_dir, "virtualenv", index_url)
            return req_cmd + " && " + venv_cmd
        else:
            return req_cmd

    @property
    def _venv_pkg_pattern(self):
        return r"^{}-.*?\.whl$".format("virtualenv")

    @staticmethod
    def _search_file(top_path, pattern):
        files = os.listdir(top_path)
        for item in files:
            if re.match(pattern, item):
                return item

    def pack(self):
        args = self._add_pack_args()
        base_dir = self._validate_base_dir(args.base_dir)
        req_dir = self._validate_req_dir(args.req_dir)
        download_dir = self._validate_download_dir(base_dir, args.download_dir)
        pack_cmd = self._get_pack_cmd(download_dir, req_dir, args.index_url, args.v)
        ret = os.system(pack_cmd)
        if ret == 0:
            output.ok("Packaged successfully! Saved {}".format(download_dir))
        else:
            output.fail("Packaged failed.")
            self._rm_download_dir(base_dir, download_dir)

    @staticmethod
    def _get_install_cmd(absolute_download_dir, req_dir=None, pkg_name=None, venv_pip_dir=None):
        if not venv_pip_dir:
            venv_pip_dir = "pip3"
        if req_dir:
            return "sudo {} install -r {} --no-index --find-links={}".format(venv_pip_dir, req_dir, absolute_download_dir)
        else:
            if pkg_name:
                return "{} install {} --no-index --find-links={}".format(venv_pip_dir, pkg_name, absolute_download_dir)
            else:
                raise MissingParamError("`req_dir` and `pkg_name` are needed at least one.")

    def _get_venv_name(self, length=8):
        return self._get_download_folder_name(length=length) + "_venv"

    def _validate_py_path(self, py_path):
        if py_path:
            if not self._is_exist_path(py_path):
                raise FileNotFoundError("the specified python interpreter path does not exist.")
            if not self._is_executable(py_path):
                raise InvalidInterpreterPathError("Invalid python interpreter path.")
            return py_path

    @staticmethod
    def _make_virtualenv_cmd(py_path, env_name):
        return "virtualenv -p {} {}".format(py_path, env_name)

    @staticmethod
    def _make_executable_cmd(venv_path):
        return "chmod +x {}/bin/activate".format(venv_path)

    def install(self):
        args = self._add_install_args()
        base_dir = self._validate_base_dir(args.base_dir)
        req_dir = self._validate_req_dir(args.req_dir)
        download_dir = self._fetch_download_dir(base_dir)
        absolute_download_dir = base_dir + "/" + download_dir
        py_path = self._validate_py_path(args.python)
        venv_pip_path = args.venv_pip_path
        if (venv_pip_path and py_path) or (not venv_pip_path and not py_path):
            raise MissingParamError("`--venv-pip-path` and `-p` must give only one.")

        if venv_pip_path:
            install_ret = os.system(self._get_install_cmd(absolute_download_dir, req_dir,
                                                          venv_pip_dir=venv_pip_path))
            if install_ret == 0:
                output.ok("installed successfully!")
            else:
                output.fail("installation project dependency failed.")
        else:
            venv_pkg_file_name = self._search_file(absolute_download_dir, self._venv_pkg_pattern)
            if venv_pkg_file_name:
                # install virtualenv
                os.chdir(absolute_download_dir)
                ret = os.system(self._get_install_cmd(absolute_download_dir, pkg_name=venv_pkg_file_name))
                if ret == 0:
                    os.chdir(base_dir)
                    # make virtualenv
                    venv_name = self._get_venv_name()
                    venv_path = base_dir + "/" + venv_name
                    build_ret = os.system(self._make_virtualenv_cmd(py_path, venv_name))
                    if build_ret == 0:
                        exe_act = os.system(self._make_executable_cmd(venv_path))
                        if exe_act == 0:
                            # install requirements
                            install_ret = os.system(self._get_install_cmd(absolute_download_dir, req_dir,
                                                                          venv_pip_dir=venv_path+"/bin/pip"))
                            if install_ret == 0:
                                output.ok("installed successfully!now you can run:\n source {}/bin/activate\nto "
                                          "activate the virtualenv.".format(venv_path))
                            else:
                                output.fail("installation project dependency failed.")
                        else:
                            output.fail("add executable permission to activate file failed.")
                    else:
                        output.fail("create virtual environment failed.")
                else:
                    output.fail("install `virtualenv` package failed.")
            else:
                raise FileNotFoundError("`virtualenv` installation package does not exist.")


env_installer = EnvInstaller()
