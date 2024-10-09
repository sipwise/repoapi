# Copyright (C) 2017-2024 The Sipwise Team - http://sipwise.com
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


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class NoConfigReleaseFile(Error):
    pass


class NoJenkinsJobsInfo(Error):
    """release config.yml has no jenkins-jobs entry"""

    pass


class NoDebianReleaseInfo(Error):
    pass


class NoReleaseInfo(Error):
    pass


class NoDistrisInfo(Error):
    pass


class NoUniqueTrunk(Error):
    """release config.yml has more than one release-trunk distri"""

    pass


class WrongTrunkDistribution(Error):
    pass


class WrongDistris(Error):
    pass


class BuildReleaseUnique(Error):
    """mrX.Y.Z release should be built just once"""

    pass


class PreviousBuildNotDone(Error):
    """same release is building right now"""

    pass


class CircularBuildDependencies(Error):
    pass
