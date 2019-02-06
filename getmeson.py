#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# Download meson to the current directory.
#
# Copyright 2019 Aman Verma
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# -----------------------------------------------------------------------------
import io
import os
import subprocess
import sys
from typing import Any

VERSION = "0.49.2"
# fmt: off
URL = "https://github.com/mesonbuild/meson/releases/download/{0}/meson-{0}.tar.gz".format(VERSION)
SHA256 = "ef9f14326ec1e30d3ba1a26df0f92826ede5a79255ad723af78a2691c37109fd"
# fmt: on
TAR_DIR = "meson-" + VERSION


def eprintf(fmtstring: str, *args: Any) -> None:
    print(fmtstring.format(*args), file=sys.stderr)


def exists(expectedversion: str) -> bool:
    mesonbinary = os.path.join("meson", "meson.py")
    if os.path.isfile(mesonbinary):
        # could throw exception, but it probably won't
        mesonver: str = subprocess.run(
            [mesonbinary, "--version"],
            check=True,
            encoding="utf-8",
            stdout=subprocess.PIPE,
        ).stdout.rstrip()
        return mesonver == expectedversion
    return False


def gettar(url: str) -> bytes:
    import urllib.error
    import urllib.request

    try:
        print("Downloading {}...".format(url))
        page = urllib.request.urlopen(url)
        return page.read()
    except urllib.error.HTTPError as e:
        eprintf("{}\nCheck if {} is up.", e.code, url)
        sys.exit(1)
    except urllib.error.URLError as e:
        eprintf("{}\nCheck your network connection.", e.reason)
        sys.exit(1)
    finally:
        page.close()


def isvalidhash(file: bytes, expectedhash: str) -> bool:
    import hashlib

    hasher = hashlib.sha256(file)
    return hasher.hexdigest() == expectedhash


def checkedrename(src: str, dst: str) -> None:
    if src != TAR_DIR:
        eprintf(
            "The archive extracted path was unexpected. "
            "Please try to extract it yourself"
        )
        sys.exit(1)
    if os.path.exists(dst):
        import shutil

        eprintf("Overwriting {}.", dst)
        shutil.rmtree(dst)

    os.rename(src, dst)


def untartodir(tar: bytes) -> None:
    import tarfile

    try:
        tarbuffered: io.BytesIO = io.BytesIO(tar)
        t = tarfile.open(fileobj=tarbuffered, mode="r")
        ogdir: str = t.getmembers()[0].name
        t.extractall()
    except tarfile.CompressionError as e:
        print(str(e), file=sys.stderr)
    else:
        checkedrename(ogdir, "meson")
    finally:
        tarbuffered.close()
        t.close()


if not exists(VERSION):
    if "-n" in sys.argv[1:]:
        eprintf(
            "Did not find meson-{} and dry run was requested.\nWould have installed {}",
            VERSION,
            URL,
        )
        sys.exit(1)
    mesontar: bytes = gettar(URL)
    if isvalidhash(mesontar, SHA256):
        untartodir(mesontar)
        print(
            "Meson should be installed. You can run it with `./meson/meson.py` on *nix"
            " and `python.exe meson\\meson.py` on Windows"
        )
    else:
        eprintf(
            "The checksum of the downloaded file does not match!\n"
            "Please download and verify the file manually."
        )
else:
    print("Found meson, skipping download.")
    sys.exit(0)
