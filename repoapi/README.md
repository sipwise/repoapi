repoapi
=======

This is the main app and where jenkins jobs results are stored.

API is documented via [swagger](https://repoapi.mgm.sipwise.com/docs/)

Models:

* [JenkinsBuildInfo](repoapi/models/jbi.py)
* [GerritRepoInfo](repoapi/models/gri.py)
* [MantisNoteInfo](repoapi/models/wni.py)

The coordination between apps is done via [signals](repoapi/signals.py) and
triggering background celery [tasks](repoapi/tasks.py)


Example workflow:

* jenkins job reports back via API POST ``jenkinsbuildinfo/``
  after the record is saved the ``post_save`` signal is triggered

```python
@receiver(
    post_save, sender="repoapi.JenkinsBuildInfo", dispatch_uid="jbi_manage"
)
def jbi_manage(sender, **kwargs):
    if kwargs["created"]:
        instance = kwargs["instance"]
        if instance.is_job_url_allowed():
            get_jbi_files.delay(
                instance.pk, instance.jobname, instance.buildnumber
            )
```

This will trigger the download of some artifacts for that build

```python
@receiver(
    post_save,
    sender="repoapi.JenkinsBuildInfo",
    dispatch_uid="gerrit_repo_manage",
)
def gerrit_repo_manage(sender, **kwargs):
```

If the job is related to '*repos' PPA management will be triggered.
We control how many project builds are in a PPA and we react on
merges or abandoned events cleaning up the PPA when necessary.

In general:

* where the API [urls](repoapi/urls.py) need to be added.
* [settings](repoapi/settings/common.py) for the Django project
  split via environment.
