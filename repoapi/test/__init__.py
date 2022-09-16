# Copyright (C) 2015-2022 The Sipwise Team - http://sipwise.com
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
import filecmp
from difflib import unified_diff
from io import StringIO
from pathlib import Path


def check_output(output_file, test_file):
    assert Path(output_file).exists()
    assert Path(test_file).exists()

    if not filecmp.cmp(output_file, test_file):
        with open(output_file) as out, open(test_file) as test:
            diff = unified_diff(
                out.readlines(),
                test.readlines(),
                fromfile=output_file,
                tofile=test_file,
            )
            for line in diff:
                print(line, end="")
        assert filecmp.cmp(output_file, test_file)


def check_stdoutput(stdout: StringIO, test_file: Path):
    assert test_file.exists()
    flag = False
    with open(test_file) as test:
        diff = unified_diff(
            stdout.getvalue().splitlines(),
            test.readlines(),
            fromfile="stdout",
            tofile=str(test_file.absolute()),
        )
        for line in diff:
            flag = True
            print(line, end="")
    assert not flag
