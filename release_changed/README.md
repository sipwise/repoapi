release_changed
===============

App keeps track of the [check-ngcp-release-changes](https://jenkins.mgm.sipwise.com/job/check-ngcp-release-changes) job result and
[matrix-runner](https://jenkins.mgm.sipwise.com/job/daily-build-matrix-runner/)
queries the API in order to decide if VM has to be built depending on if the repository has changed since the last successful VM built.
